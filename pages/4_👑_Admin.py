"""
Admin Panel - User Management
Only accessible to users with role = 'admin'
"""

import streamlit as st
from auth.auth_manager import require_auth, get_auth_manager

st.set_page_config(
    page_title="Admin - Sales Chatbot",
    page_icon="👑",
    layout="wide"
)


def main():
    require_auth()

    # Only admins can access this page
    if st.session_state.get("user_role") != "admin":
        st.error("Access denied. Admin only.")
        st.stop()

    auth = get_auth_manager()

    st.title("👑 Admin Panel")

    # Supabase connection status
    if auth.is_supabase_connected():
        st.success("✅ Connected to Supabase")
    else:
        st.warning("⚠️ Using local auth (Supabase not configured). Add credentials to .env to enable Supabase.")

    st.markdown("---")

    # ── Section 1: Add New User ────────────────────────────────────────────────
    st.subheader("➕ Add New User")

    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input(
                "Email" if auth.is_supabase_connected() else "Username",
                placeholder="e.g. john@company.com"
            )
            new_name = st.text_input("Full Name", placeholder="e.g. John Smith")
        with col2:
            new_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            new_role = st.selectbox("Role", ["user", "admin"])

        submitted = st.form_submit_button("Create User", type="primary")
        if submitted:
            if not new_email or not new_password or not new_name:
                st.error("Please fill in all fields.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                success, msg = auth.add_user(new_email, new_password, new_name, new_role)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.markdown("---")

    # ── Section 2: Manage Existing Users ─────────────────────────────────────
    st.subheader("👥 Manage Users")

    users = auth.list_users()

    if not users:
        st.info("No users found.")
        return

    current_username = st.session_state.get("username")

    for user in users:
        is_self = user["email"] == current_username
        status_icon = "🟢" if user["active"] else "🔴"
        role_badge = "👑 Admin" if user["role"] == "admin" else "👤 User"

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1.5])

            with col1:
                st.markdown(f"{status_icon} **{user['name']}**  \n`{user['email']}` · {role_badge} · Joined: {user['created_at']}")

            with col2:
                if is_self:
                    st.caption("(You)")
                elif user["active"]:
                    if st.button("🔴 Deactivate", key=f"deact_{user['id']}", use_container_width=True):
                        success, msg = auth.set_user_active(str(user["id"]), False)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    if st.button("🟢 Activate", key=f"act_{user['id']}", use_container_width=True):
                        success, msg = auth.set_user_active(str(user["id"]), True)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            with col3:
                st.caption("")  # spacer

            with col4:
                if not is_self:
                    if st.button("🗑️ Delete", key=f"del_{user['id']}", use_container_width=True):
                        success, msg = auth.delete_user(str(user["id"]))
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            st.divider()


main()
