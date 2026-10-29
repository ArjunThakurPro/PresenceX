import textwrap

import streamlit as st

CARD_STYLES = """
<style>
.subject-card {
    box-sizing: border-box;
    width: 100%;
    min-height: 270px;
    padding: 24px;
    margin: 0 0 16px;
    overflow: hidden;
    color: #14213d;
    background: linear-gradient(145deg, #ffffff 0%, #f1f6ff 100%);
    border: 1px solid #dce7f7;
    border-radius: 22px;
    box-shadow: 0 12px 30px rgba(31, 65, 114, 0.09);
}
.subject-card__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
}
.subject-card__eyebrow {
    color: #52709b;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.13em;
}
.subject-card__code {
    padding: 7px 11px;
    color: #2456a6;
    background: #e5efff;
    border: 1px solid #d4e4ff;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
}
.subject-card__title {
    margin: 0 0 20px;
    color: #14213d;
    font-size: 1.45rem;
    font-weight: 750;
    line-height: 1.25;
    overflow-wrap: anywhere;
}
.subject-card__details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 18px;
}
.subject-card__detail {
    min-width: 0;
    padding: 11px 13px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid #e6edf7;
    border-radius: 13px;
}
.subject-card__label {
    display: block;
    margin-bottom: 4px;
    color: #71819a;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.subject-card__value {
    display: block;
    color: #263a5b;
    font-size: 0.92rem;
    font-weight: 650;
    overflow-wrap: anywhere;
}
.subject-card__stats {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.subject-card__stat {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 12px 14px;
    color: #263a5b;
    background: #eaf2ff;
    border-radius: 14px;
}
.subject-card__icon {
    font-size: 1.25rem;
}
.subject-card__stat-label {
    display: block;
    color: #627694;
    font-size: 0.72rem;
}
.subject-card__stat-value {
    display: block;
    color: #1d4f98;
    font-size: 1.05rem;
    font-weight: 750;
}
.subject-card__empty-stats {
    padding: 12px 14px;
    color: #627694;
    background: #eaf2ff;
    border-radius: 14px;
    font-size: 0.85rem;
}
@media (max-width: 480px) {
    .subject-card { padding: 18px; }
    .subject-card__title { font-size: 1.25rem; }
}
</style>
"""


def _escape_html(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def subject_card(
    subject_name,
    subject_code,
    program,
    section,
    stats=None,
    footer_callback=None,
):
    safe_name = _escape_html(subject_name or "Untitled subject")
    safe_code = _escape_html(subject_code or "No code")
    safe_program = _escape_html(program or "Not specified")
    safe_section = _escape_html(section or "Not specified")

    if stats:
        stat_items = []
        for icon, label, value in stats:
            safe_icon = _escape_html(icon)
            safe_label = _escape_html(label)
            safe_value = _escape_html(value)
            stat_items.append(
                textwrap.dedent(
                    """\
                    <div class="subject-card__stat">
                        <span class="subject-card__icon">{safe_icon}</span>
                        <span>
                            <span class="subject-card__stat-label">{safe_label}</span>
                            <span class="subject-card__stat-value">{safe_value}</span>
                        </span>
                    </div>
                """
                ).format(
                    safe_icon=safe_icon,
                    safe_label=safe_label,
                    safe_value=safe_value,
                )
            )
        stats_markup = "".join(stat_items)
    else:
        stats_markup = (
            '<div class="subject-card__empty-stats">No stats available yet</div>'
        )

    card_markup = textwrap.dedent(
        """\
        <article class="subject-card">
            <div class="subject-card__top">
                <span class="subject-card__eyebrow">SUBJECT</span>
                <span class="subject-card__code">{safe_code}</span>
            </div>
            <h3 class="subject-card__title">{safe_name}</h3>
            <div class="subject-card__details">
                <div class="subject-card__detail">
                    <span class="subject-card__label">Program</span>
                    <span class="subject-card__value">{safe_program}</span>
                </div>
                <div class="subject-card__detail">
                    <span class="subject-card__label">Section</span>
                    <span class="subject-card__value">{safe_section}</span>
                </div>
            </div>
            <div class="subject-card__stats">{stats_markup}</div>
        </article>
        """
    ).format(
        safe_code=safe_code,
        safe_name=safe_name,
        safe_program=safe_program,
        safe_section=safe_section,
        stats_markup=stats_markup,
    )

    st.markdown(
        CARD_STYLES + "\n" + card_markup,
        unsafe_allow_html=True,
    )

    if footer_callback is not None:
        footer_callback()
