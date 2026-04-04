import vertexai
from vertexai.generative_models import GenerativeModel


def init_model(project: str, region: str, model_name: str) -> GenerativeModel:
    """Initialize Vertex AI and return a GenerativeModel instance."""
    vertexai.init(project=project, location=region)
    return GenerativeModel(model_name)


def summarize(model: GenerativeModel, text: str, title: str) -> str:
    """Generate a 3-5 sentence summary of an article for a technical audience."""
    prompt = (
        f"Summarize the following blog post titled '{title}' in 3-5 sentences "
        f"for a technical audience. Focus on the key insights and any practical "
        f"takeaways:\n\n{text}"
    )
    response = model.generate_content(prompt)
    return response.text
