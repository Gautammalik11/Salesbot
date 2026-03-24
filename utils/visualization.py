"""
Visualization helpers for creating charts and graphs.
Uses Plotly for interactive visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
import pandas as pd


def create_bar_chart(
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str = "",
    y_label: str = "",
    color: str = "#636EFA"
) -> go.Figure:
    """Create a bar chart.

    Args:
        data: List of data dictionaries
        x_field: Field name for x-axis
        y_field: Field name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Bar color

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    fig = go.Figure(data=[
        go.Bar(
            x=df[x_field],
            y=df[y_field],
            marker_color=color,
            text=df[y_field],
            texttemplate='%{text:.2f}',
            textposition='outside'
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        height=400,
        template="plotly_white"
    )

    return fig


def create_horizontal_bar_chart(
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str = "",
    y_label: str = "",
    color: str = "#636EFA"
) -> go.Figure:
    """Create a horizontal bar chart.

    Args:
        data: List of data dictionaries
        x_field: Field name for x-axis (values)
        y_field: Field name for y-axis (categories)
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Bar color

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    fig = go.Figure(data=[
        go.Bar(
            x=df[x_field],
            y=df[y_field],
            orientation='h',
            marker_color=color,
            text=df[x_field],
            texttemplate='%{text:.2f}',
            textposition='outside'
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        height=max(400, len(df) * 30),
        template="plotly_white"
    )

    return fig


def create_line_chart(
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str = "",
    y_label: str = "",
    color: str = "#636EFA"
) -> go.Figure:
    """Create a line chart for trends.

    Args:
        data: List of data dictionaries
        x_field: Field name for x-axis
        y_field: Field name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Line color

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    fig = go.Figure(data=[
        go.Scatter(
            x=df[x_field],
            y=df[y_field],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8),
            text=df[y_field],
            hovertemplate='%{x}<br>%{text:.2f}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=False,
        height=400,
        template="plotly_white"
    )

    return fig


def create_pie_chart(
    data: List[Dict[str, Any]],
    names_field: str,
    values_field: str,
    title: str,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """Create a pie chart.

    Args:
        data: List of data dictionaries
        names_field: Field name for pie slice labels
        values_field: Field name for pie slice values
        title: Chart title
        colors: List of colors for pie slices

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    fig = go.Figure(data=[
        go.Pie(
            labels=df[names_field],
            values=df[values_field],
            marker=dict(colors=colors) if colors else None,
            textinfo='label+percent',
            hovertemplate='%{label}<br>%{value:.2f}<br>%{percent}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=title,
        height=400,
        template="plotly_white"
    )

    return fig


def create_multi_line_chart(
    data: List[Dict[str, Any]],
    x_field: str,
    y_fields: List[str],
    title: str,
    x_label: str = "",
    y_label: str = "",
    labels: Optional[List[str]] = None
) -> go.Figure:
    """Create a multi-line chart for comparing trends.

    Args:
        data: List of data dictionaries
        x_field: Field name for x-axis
        y_fields: List of field names for y-axis lines
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        labels: Custom labels for each line

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    fig = go.Figure()

    if not labels:
        labels = y_fields

    for i, y_field in enumerate(y_fields):
        fig.add_trace(go.Scatter(
            x=df[x_field],
            y=df[y_field],
            mode='lines+markers',
            name=labels[i],
            line=dict(width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=400,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_metric_card(
    value: float,
    label: str,
    prefix: str = "",
    suffix: str = "",
    delta: Optional[float] = None,
    delta_label: str = ""
) -> str:
    """Create HTML for a metric card.

    Args:
        value: Metric value
        label: Metric label
        prefix: Prefix (e.g., '$')
        suffix: Suffix (e.g., '%')
        delta: Change value (optional)
        delta_label: Label for delta (optional)

    Returns:
        HTML string
    """
    formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"

    html = f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="margin: 0; color: #636EFA; font-size: 2.5em;">{prefix}{formatted_value}{suffix}</h3>
        <p style="margin: 10px 0 0 0; color: #31333F; font-size: 1.2em;">{label}</p>
    """

    if delta is not None:
        delta_color = "green" if delta >= 0 else "red"
        delta_symbol = "↑" if delta >= 0 else "↓"
        html += f"""
        <p style="margin: 5px 0 0 0; color: {delta_color}; font-size: 0.9em;">
            {delta_symbol} {abs(delta):.2f}% {delta_label}
        </p>
        """

    html += "</div>"
    return html


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format amount as currency.

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol

    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"


def create_table_figure(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    title: str = ""
) -> go.Figure:
    """Create an interactive table using Plotly.

    Args:
        data: List of data dictionaries
        columns: List of column names to display (optional)
        title: Table title

    Returns:
        Plotly Figure object
    """
    df = pd.DataFrame(data)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig

    if columns:
        df = df[columns]

    # Format numeric columns
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='#636EFA',
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color='#f0f2f6',
            align='left',
            font=dict(size=11)
        )
    )])

    fig.update_layout(
        title=title,
        height=min(600, max(200, len(df) * 30 + 100)),
        template="plotly_white"
    )

    return fig
