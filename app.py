import gradio as gr
from backend.utils import (
    generate_quiz,
    get_closed_book_answers,
    get_web_rag_answers_and_snippets,
)


def goto_llm_tab():
    return gr.Tabs(selected="llm_tab")


def populate_quiz(quiz, url):
    quiz = None
    max_tries = 2
    tries = 0

    while quiz is None and tries < max_tries:
        try:
            quiz = generate_quiz(url)
        except:
            tries += 1
    quiz_header = gr.Markdown("## 📝 Quiz")

    options, md_blocks = [], []
    for i in range(5):
        option = gr.Radio(
            value=None,
            choices=quiz["questions"][i]["options"],
            interactive=True,
            label=quiz["questions"][i]["question"],
            visible=True,
        )
        options.append(option)
        md_blocks.append(gr.Markdown(visible=False))

    submit_btn = gr.Button(value="Submit", variant="primary", visible=True)
    let_llm_play_btn = gr.Button(visible=True, value="🤖 Let the LLM play 🎮")
    score_label = gr.Label(visible=False)

    llm_tab = gr.TabItem("🤖 Let the LLM play 🎮", id="llm_tab", visible=True)
    closed_book_btn = gr.Button(value="Try", visible=True, variant="primary")
    closed_score_label = gr.Label("Results")
    closed_book_accordion = gr.Accordion(visible=False)
    web_rag_btn = gr.Button(value="Try", visible=True, variant="primary")
    web_score_label = gr.Label("Results")
    web_rag_accordion = gr.Accordion(visible=False)

    return (
        quiz,
        quiz_header,
        *options,
        *md_blocks,
        submit_btn,
        let_llm_play_btn,
        score_label,
        llm_tab,
        closed_book_btn,
        closed_score_label,
        closed_book_accordion,
        web_rag_btn,
        web_score_label,
        web_rag_accordion,
    )


def compute_display_results(quiz, answer0, answer1, answer2, answer3, answer4):

    md_blocks = []
    score = 0

    for i, answer in enumerate([answer0, answer1, answer2, answer3, answer4]):
        right_option = quiz["questions"][i]["right_option"]
        if isinstance(answer, str) and answer[0] == right_option:
            score += 1
            md_blocks.append(gr.Markdown("Correct", visible=True))
        else:
            md_blocks.append(
                gr.Markdown("Wrong. Correct answer: " + right_option, visible=True)
            )

    score = score / 5

    score_label = gr.Label(
        f"Your score is {score*100}%", visible=True, show_label=False
    )

    options = []
    for i in range(5):
        option = gr.Radio(
            choices=quiz["questions"][i]["options"],
            interactive=False,
            label=quiz["questions"][i]["question"],
            visible=True,
        )
        options.append(option)

    submit_btn = gr.Button(visible=False)

    return score_label, *md_blocks, *options, submit_btn


def compute_display_closed_book(quiz):

    answers = get_closed_book_answers(quiz)

    details = ""

    score = 0
    for i, answer in enumerate(answers):
        details += f"**Question**: {quiz['questions'][i]['question']}\n\n"
        details += f"**Answer from LLM**: {quiz['questions'][i]['options'][ord(answer) - ord('a')]}\n\n"
        details += f"**Correct answer**: {quiz['questions'][i]['options'][ord(quiz['questions'][i]['right_option']) - ord('a')]}\n\n"
        details += "---\n\n"
        if answer == quiz["questions"][i]["right_option"]:
            score += 1

    score = score / 5

    closed_book_label = gr.Label(
        f"LLM closed book score is {score*100}%", visible=True, show_label=False
    )

    closed_book_btn = gr.Button(visible=False)

    closed_book_accordion = gr.Accordion("Details", visible=True, open=False)
    closed_book_details = gr.Markdown(details, visible=True)

    return (
        closed_book_label,
        closed_book_btn,
        closed_book_accordion,
        closed_book_details,
    )


def compute_display_web_rag(quiz):

    answers, snippets = get_web_rag_answers_and_snippets(quiz)

    details = ""
    score = 0
    for i, answer in enumerate(answers):
        details += f"**Question**: {quiz['questions'][i]['question']}\n\n"
        details += f"**Answer from LLM**: {quiz['questions'][i]['options'][ord(answer) - ord('a')]}\n\n"
        details += f"**Correct answer**: {quiz['questions'][i]['options'][ord(quiz['questions'][i]['right_option']) - ord('a')]}\n\n"
        details += f"**Top 3 snippets from Google search**:\n\n"
        for snippet in snippets[i]:
            details += f"- {snippet}\n"
        details += "---\n\n"
        if answer == quiz["questions"][i]["right_option"]:
            score += 1

    score = score / 5

    web_rag_label = gr.Label(
        f"LLM Web RAG score is {score*100}%", visible=True, show_label=False
    )

    web_rag_btn = gr.Button(visible=False)

    web_rag_accordion = gr.Accordion("Details", visible=True, open=False)
    web_rag_details = gr.Markdown(details, visible=True)

    return web_rag_label, web_rag_btn, web_rag_accordion, web_rag_details


# Gradio app

HEADER = """
<div align="center">
  <p style="font-size: 44px;">🧑‍🏫 AutoQuizzer</p>
  <p style="font-size: 25px;">AutoQuizzer generates a quiz from a URL. You can play the quiz, or let the LLM play it.</p>
  <p style="font-size: 20px;"><b>Built using: <a href="https://haystack.deepset.ai/">🏗️ Haystack</a> • 🦙 Llama 3 8B Instruct • ⚡ Groq</b></p>
</div>
"""

URL_EXAMPLES = [
    "https://www.reuters.com/technology/microsoft-agreed-pay-inflection-650-mln-while-hiring-its-staff-information-2024-03-21/",
    "https://www.rainforest-alliance.org/species/capybara/",
    "https://en.wikipedia.org/wiki/Predator_(film)",
    "https://lite.cnn.com/2024/04/22/entertainment/zendaya-challengers-in/index.html",
    "https://en.wikipedia.org/wiki/The_Cure",
    "https://www.bloomberg.com/news/newsletters/2024-05-14/game-makers-at-midsummer-studios-look-to-take-on-the-sims",
    "https://www.rainforest-alliance.org/species/howler-monkey/",
]

with open("README.md", "r") as fin:
    info_md = (
        fin.read()
        .split("<!--- Include in Info tab -->")[-1]
        .replace("autoquizzer.png", "/file=autoquizzer.png")
    )


with gr.Blocks(theme=gr.themes.Soft(primary_hue="sky")) as demo:
    gr.Markdown(HEADER)
    quiz = gr.State({})
    with gr.Tabs() as tabs:
        with gr.TabItem("Generate quiz and play"):
            with gr.Row():
                url = gr.Textbox(
                    label="URL from which to generate a quiz",
                    value=URL_EXAMPLES[0],
                    interactive=True,
                    max_lines=1,
                )
                generate_quiz_btn = gr.Button(
                    value="Generate quiz", variant="primary", scale=0
                )

            examples = gr.Examples(
                examples=URL_EXAMPLES,
                inputs=[url],
                label=["Example URLs"],
            )

            quiz_header = gr.Markdown("## 📝 Quiz")
            with gr.Row():
                options0 = gr.Radio(visible=False)
                mdblock0 = gr.Markdown(visible=False)
            with gr.Row():
                options1 = gr.Radio(visible=False)
                mdblock1 = gr.Markdown(visible=False)
            with gr.Row():
                options2 = gr.Radio(visible=False)
                mdblock2 = gr.Markdown(visible=False)
            with gr.Row():
                options3 = gr.Radio(visible=False)
                mdblock3 = gr.Markdown(visible=False)
            with gr.Row():
                options4 = gr.Radio(visible=False)
                mdblock4 = gr.Markdown(visible=False)
            with gr.Row():
                submit_btn = gr.Button(visible=False)
                let_llm_play_btn = gr.Button(visible=False)
            with gr.Row():
                score_label = gr.Label(visible=False)

        with gr.TabItem(id="llm_tab", visible=False) as llm_tab:

            gr.Markdown("## 📕 Closed book exam")
            gr.Markdown(
                "Llama3 is given only the topic and questions. It will answer based on its parametric knowledge and reasoning abilities."
            )

            closed_book_btn = gr.Button(visible=False)
            closed_score_label = gr.Label("Results", show_label=False)
            with gr.Accordion(visible=False) as closed_book_accordion:
                md_closed_book_details = gr.Markdown(visible=False)

            gr.Markdown("## 🔎🌐 Web RAG")
            gr.Markdown(
                "The top 3 snippets from Google search are included in the prompt."
            )
            web_rag_btn = gr.Button(visible=False)
            web_score_label = gr.Label("Results", show_label=False)
            with gr.Accordion(visible=False) as web_rag_accordion:
                md_web_rag_details = gr.Markdown(visible=False)

        with gr.TabItem("ℹ️ Info", id="info") as info_tab:
            gr.Markdown(info_md)

        closed_book_btn.click(
            fn=compute_display_closed_book,
            inputs=[quiz],
            outputs=[
                closed_score_label,
                closed_book_btn,
                closed_book_accordion,
                md_closed_book_details,
            ],
        )
        web_rag_btn.click(
            fn=compute_display_web_rag,
            inputs=[quiz],
            outputs=[
                web_score_label,
                web_rag_btn,
                web_rag_accordion,
                md_web_rag_details,
            ],
        )
        generate_quiz_btn.click(
            fn=populate_quiz,
            inputs=[quiz, url],
            outputs=[
                quiz,
                quiz_header,
                options0,
                options1,
                options2,
                options3,
                options4,
                mdblock0,
                mdblock1,
                mdblock2,
                mdblock3,
                mdblock4,
                submit_btn,
                let_llm_play_btn,
                score_label,
                llm_tab,
                closed_book_btn,
                closed_score_label,
                closed_book_accordion,
                web_rag_btn,
                web_score_label,
                web_rag_accordion,
            ],
        )
        submit_btn.click(
            fn=compute_display_results,
            inputs=[quiz, options0, options1, options2, options3, options4],
            outputs=[
                score_label,
                mdblock0,
                mdblock1,
                mdblock2,
                mdblock3,
                mdblock4,
                options0,
                options1,
                options2,
                options3,
                options4,
                submit_btn,
            ],
        )
        let_llm_play_btn.click(fn=goto_llm_tab, inputs=[], outputs=tabs)


demo.queue(default_concurrency_limit=5).launch(
    show_api=False, server_name="0.0.0.0", allowed_paths=["/"]
)


demo.launch()
