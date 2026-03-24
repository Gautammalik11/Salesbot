"""
Authentication Manager - Supabase
Handles login/logout using Supabase Auth.
Falls back to local JSON users if Supabase is not configured.
"""

import hashlib
import json
import os
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Check if Supabase is configured
USE_SUPABASE = bool(
    SUPABASE_URL and SUPABASE_URL != "your_project_url_here" and
    SUPABASE_ANON_KEY and SUPABASE_ANON_KEY != "your_anon_key_here"
)

# ─────────────────────────────────────────────
# Local fallback (used until Supabase is set up)
# ─────────────────────────────────────────────
USERS_FILE = Path(__file__).parent / "users.json"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_local_users() -> list:
    if not USERS_FILE.exists():
        default_users = [
            {
                "username": "admin",
                "password_hash": _hash_password("admin123"),
                "name": "Admin",
                "role": "admin",
                "active": True
            }
        ]
        with open(USERS_FILE, "w") as f:
            json.dump(default_users, f, indent=2)
        return default_users

    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_local_users(users: list):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ─────────────────────────────────────────────
# AuthManager
# ─────────────────────────────────────────────
class AuthManager:
    def __init__(self):
        if USE_SUPABASE:
            from supabase import create_client
            self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            self.admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) if SUPABASE_SERVICE_ROLE_KEY else None
        else:
            self.client = None
            self.admin_client = None
            self.local_users = _load_local_users()

    # ── Login ─────────────────────────────────────────────────────────────────

    def authenticate(self, email_or_username: str, password: str) -> Optional[Dict[str, Any]]:
        if USE_SUPABASE:
            return self._authenticate_supabase(email_or_username, password)
        return self._authenticate_local(email_or_username, password)

    def _authenticate_supabase(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user = response.user
            if user:
                meta = user.user_metadata or {}
                return {
                    "id": user.id,
                    "username": email,
                    "name": meta.get("name", email.split("@")[0]),
                    "role": meta.get("role", "user"),
                    "email": email,
                }
            return None
        except Exception as e:
            err = str(e).lower()
            if "invalid" in err or "credentials" in err or "email" in err:
                return None
            raise e

    def _authenticate_local(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        pw_hash = _hash_password(password)
        for user in self.local_users:
            if user["username"] == username and user["password_hash"] == pw_hash:
                if not user.get("active", True):
                    return "deactivated"
                return user
        return None

    # ── Logout ────────────────────────────────────────────────────────────────

    def logout(self):
        if USE_SUPABASE:
            try:
                self.client.auth.sign_out()
            except Exception:
                pass
        for key in ["logged_in", "user", "username", "user_name", "user_role", "user_email"]:
            st.session_state.pop(key, None)

    # ── Admin: List users ─────────────────────────────────────────────────────

    def list_users(self) -> list:
        if USE_SUPABASE and self.admin_client:
            try:
                response = self.admin_client.auth.admin.list_users()
                users = []
                for u in response:
                    meta = u.user_metadata or {}
                    users.append({
                        "id": u.id,
                        "email": u.email,
                        "name": meta.get("name", u.email),
                        "role": meta.get("role", "user"),
                        "active": u.banned_until is None,
                        "created_at": str(u.created_at)[:10],
                    })
                return users
            except Exception as e:
                st.error(f"Error listing users: {e}")
                return []
        # Local fallback
        return [
            {
                "id": i,
                "email": u.get("username"),
                "name": u.get("name"),
                "role": u.get("role"),
                "active": u.get("active", True),
                "created_at": "-",
            }
            for i, u in enumerate(self.local_users)
        ]

    # ── Admin: Add user ───────────────────────────────────────────────────────

    def add_user(self, email: str, password: str, name: str, role: str = "user") -> tuple:
        """Returns (success: bool, message: str)"""
        if USE_SUPABASE and self.admin_client:
            try:
                self.admin_client.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"name": name, "role": role}
                })
                return True, f"User '{name}' created successfully."
            except Exception as e:
                return False, str(e)
        # Local fallback
        self.local_users = _load_local_users()
        for u in self.local_users:
            if u["username"] == email:
                return False, "Username already exists."
        self.local_users.append({
            "username": email,
            "password_hash": _hash_password(password),
            "name": name,
            "role": role,
            "active": True,
        })
        _save_local_users(self.local_users)
        return True, f"User '{name}' created successfully."

    # ── Admin: Deactivate / Reactivate user ───────────────────────────────────

    def set_user_active(self, user_id: str, active: bool) -> tuple:
        """Returns (success: bool, message: str)"""
        if USE_SUPABASE and self.admin_client:
            try:
                if active:
                    self.admin_client.auth.admin.update_user_by_id(
                        user_id, {"ban_duration": "none"}
                    )
                else:
                    self.admin_client.auth.admin.update_user_by_id(
                        user_id, {"ban_duration": "876600h"}  # ~100 years
                    )
                action = "activated" if active else "deactivated"
                return True, f"User {action} successfully."
            except Exception as e:
                return False, str(e)
        # Local fallback
        self.local_users = _load_local_users()
        for u in self.local_users:
            if str(u.get("id", u.get("username"))) == str(user_id):
                u["active"] = active
                _save_local_users(self.local_users)
                action = "activated" if active else "deactivated"
                return True, f"User {action} successfully."
        return False, "User not found."

    # ── Admin: Delete user ────────────────────────────────────────────────────

    def delete_user(self, user_id: str) -> tuple:
        """Returns (success: bool, message: str)"""
        if USE_SUPABASE and self.admin_client:
            try:
                self.admin_client.auth.admin.delete_user(user_id)
                return True, "User deleted."
            except Exception as e:
                return False, str(e)
        # Local fallback
        self.local_users = _load_local_users()
        self.local_users = [
            u for u in self.local_users
            if str(u.get("id", u.get("username"))) != str(user_id)
        ]
        _save_local_users(self.local_users)
        return True, "User deleted."

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_supabase_connected(self) -> bool:
        return USE_SUPABASE

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        if st.session_state.get("logged_in"):
            return {
                "username": st.session_state.get("username"),
                "name": st.session_state.get("user_name"),
                "role": st.session_state.get("user_role"),
            }
        return None


# ─────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────
_auth_manager = None


def get_auth_manager() -> AuthManager:
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# ─────────────────────────────────────────────
# Login UI + page guard
# ─────────────────────────────────────────────
def require_auth():
    """Call at the top of every page. Shows login screen if not authenticated."""
    if not st.session_state.get("logged_in"):
        _show_login_page()
        st.stop()


def _show_login_page():
    auth = get_auth_manager()

    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
            .block-container { max-width: 420px; margin: auto; padding-top: 80px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; margin-bottom: 8px;">
            <span style="font-size: 56px;">💬</span>
        </div>
        <h2 style="text-align:center; margin-bottom: 4px;">Sales Chatbot</h2>
        <p style="text-align:center; color: #888; margin-bottom: 32px;">
            Sign in to access your dashboard
        </p>
    """, unsafe_allow_html=True)

    label = "Email" if auth.is_supabase_connected() else "Username"

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(label, placeholder=f"Enter your {label.lower()}")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please enter both fields.")
            else:
                result = auth.authenticate(username.strip(), password)
                if result == "deactivated":
                    st.error("Your account has been deactivated. Contact your admin.")
                elif result:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = result["username"]
                    st.session_state["user_name"] = result["name"]
                    st.session_state["user_role"] = result["role"]
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

    if not auth.is_supabase_connected():
        st.markdown("""
            <p style="text-align:center; color: #aaa; font-size: 12px; margin-top: 32px;">
                Default: admin / admin123
            </p>
        """, unsafe_allow_html=True)
