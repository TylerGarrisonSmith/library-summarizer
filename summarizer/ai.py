from google import genai


def init_model(project: str, region: str, model_name: str) -> genai.Client:
    """Initialize and return a Vertex AI generative AI client."""
    return genai.Client(vertexai=True, project=project, location=region)


def summarize(client: genai.Client, model_name: str, text: str, title: str) -> str:
    """Generate a 3-5 sentence summary of an article for a technical audience."""
    prompt = (
        f"Summarize the following blog post titled '{title}' in 3-5 sentences "
        f"for a technical audience. Focus on the key insights and any practical "
        f"takeaways:\n\n{text}"
    )
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text
