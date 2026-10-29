import streamlit as st
import base64


def style_background_home():
    with open("bg.png", "rb") as file:
        img = base64.b64encode(file.read()).decode()

    st.markdown(
        f"""
        <style>

        /* =========================
           MAIN BACKGROUND
        ========================= */
        .stApp {{
                    background-image: url("data:image/png;base64,{img}") !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-repeat: no-repeat !important;
                    background-attachment: fixed !important;
                }}


        /* =========================
           PORTAL CARDS
        ========================= */

        .st-key-teacher_card,
        .st-key-student_card {{

            background: #E0E3FF !important;

            border-radius: 2.5rem !important;

            padding: 1rem !important;

            box-shadow:
                0 10px 25px rgba(0, 0, 0, 0.12) !important;

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease !important;
        }}


        /* Card hover */

        .st-key-teacher_card:hover,
        .st-key-student_card:hover {{

            transform: translateY(-6px) !important;

            box-shadow:
                0 18px 35px rgba(0, 0, 0, 0.18) !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def style_background_dashboard():
    st.markdown(
        """
    <style>
    .stApp{
        background: #E0E3FF !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def style_teacher_dashboard():
    st.markdown(
        """
        <style>
        .st-key-teacher_dashboard {
            max-width: 1120px;
            margin: 0 auto;
            padding: 0.5rem 0.25rem 2rem;
        }

        .st-key-teacher_hero {
            padding: clamp(1rem, 3vw, 2rem);
            margin-bottom: 1.25rem;
            background: linear-gradient(135deg, #ffffff 0%, #f4f3ff 100%);
            border: 2px solid rgba(99, 102, 241, 0.16);
            border-radius: 28px;
            box-shadow: 0 18px 45px rgba(65, 56, 150, 0.10);
        }

        .st-key-teacher_hero h1 {
            margin: 0.15rem 0 0.4rem;
            color: #25205f !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: clamp(1.5rem, 3vw, 2.25rem) !important;
            line-height: 1.15 !important;
        }

        .st-key-teacher_hero [data-testid="stCaptionContainer"] p {
            color: #6b6890 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        .st-key-teacher_navigation {
            padding: 0.4rem;
            margin-bottom: 1.1rem;
            background: rgba(255, 255, 255, 0.66);
            border: 6px solid rgba(99, 102, 241, 0.12);
            border-radius: 20px;
        }

        .st-key-teacher_dashboard button[kind="primary"],
        .st-key-teacher_dashboard button[kind="secondary"] {
            min-height: 2.9rem;
            border-radius: 25px !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 650 !important;
        }

        .st-key-teacher_dashboard button[kind="primary"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, #625bf6, #4841c8) !important;
            border: 2px solid #5149dc !important;
            box-shadow: 0 8px 18px rgba(79, 70, 229, 0.2) !important;
        }

        .st-key-teacher_dashboard button[kind="secondary"] {
            color: #443da7 !important;
            background: #ffffff !important;
            border: 2px solid #deddf8 !important;
        }

        .st-key-teacher_actions .st-key-bt1,
        .st-key-teacher_actions .st-key-bt2 {
            margin-bottom: 0.65rem;
        }

        .st-key-teacher_actions .st-key-bt2 button {
            color: #a83232 !important;
            background: #fff1f0 !important;
            border-color: #f2c3bf !important;
        }

        .st-key-teacher_dashboard button:focus-visible {
            outline: 3px solid #a5b4fc !important;
            outline-offset: 2px !important;
        }

        .st-key-teacher_content {
            min-height: 280px;
            padding: clamp(1rem, 2.5vw, 1.75rem);
            background: rgba(255, 255, 255, 0.88);
            border: 2px solid rgba(99, 102, 241, 0.14);
            border-radius: 24px;
            box-shadow: 0 14px 36px rgba(65, 56, 150, 0.08);
        }

        .st-key-teacher_content h1,
        .st-key-teacher_content h2,
        .st-key-teacher_content h3 {
            color: #25205f !important;
            font-family: 'Outfit', sans-serif !important;
        }

        .st-key-teacher_content [data-testid="stCaptionContainer"] p {
            color: #6b6890 !important;
        }

        .st-key-teacher_content [data-testid="stCameraInput"] {
            padding: 0.75rem;
            background: #f7f7ff;
            border: 1px dashed #b8b4f4;
            border-radius: 18px;
        }

        @media (max-width: 700px) {
            .st-key-teacher_dashboard {
                padding: 0.25rem 0 1.25rem;
            }

            .st-key-teacher_hero,
            .st-key-teacher_content {
                border-radius: 20px;
            }

            .st-key-teacher_navigation {
                padding: 0.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def dialog_dashboard():
    st.markdown(
        """
        <style>
        .st-dialog {
            max-width: 600px;
            margin: 0 auto;
            padding: 1rem;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 18px 45px rgba(65, 56, 150, 0.10);
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
                /* Hide top bar of streamlit */
                #MainMenu, footer, header{
                    visibility : hidden;
                }
                .block-container{ 
                    padding-top : 1rem !important;
                }
                 h2{
                    font-family : 'climate crisis' ,sans-serif !important;
                    font-size : 1.5rem !important; 
                    line-height : 2rem !important;
                    margin-bottom : 1rem !important;
                    color : black !important;
                    }
    </style>
        """,
        unsafe_allow_html=True,
    )


def style_base_layout():
    st.markdown(
        """
               <style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Changa+One:ital@0;1&display=swap');
                /* Hide top bar of streamlit */
                #MainMenu, footer, header{
                    visibility : hidden;
                }
                .block-container{ 
                    padding-top : 1rem !important;
                }
                 h2{
                    font-family : 'changa one' ,sans-serif !important;
                    font-size : 1.5rem !important; 
                    line-height : 2rem !important;
                    margin-bottom : 1rem !important;
                    color : black !important;
                    }
                h1{
                    font-family : 'changa one', sans-serif !important;
                    font-size : 1.5rem !important;
                    line-height : 2.5rem !important;
                    margin-bottom : 1rem !important;
                    color : blue !important;
                    }

                button[kind = "primary"]{
                    border-radius :1.5rem !important;
                    background :red !important;
                    padding :10px 20px !important;
                    transition: transform 0.25s ease-in-out !important;
                }
                button[kind = "secondary"]{
                                    border-radius :1.5rem !important;
                                    background :#5865F2 !important;
                                    padding :10px 20px !important;
                                    transition: transform 0.25s ease-in-out !important;
                                }
                
                button:hover {

            transform: translateY(-2px) !important;

            box-shadow:
                0 8px 18px rgba(0, 0, 0, 0.18) !important;

        }
        /* Input box */
        div[data-baseweb="input"] {
            background-color: blue !important;
            border-radius: 12px !important;
        }

        /* Text inside input */
        div[data-baseweb="input"] input {
            color: black !important;
        }

        /* Placeholder text */
        div[data-baseweb="input"] input::placeholder {
            color: #64748B !important;
            opacity: 1 !important;
        }
        div[data-testid="stTextInput"] label {
    color: #000000 !important;
    font-weight: 600;
}  

               </style>
                """,
        unsafe_allow_html=True,
    )
