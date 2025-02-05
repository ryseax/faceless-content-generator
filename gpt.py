import openai
from openai import OpenAI
import KEYS

openai.api_key = KEYS.OPEN_AI_API_KEY
client = OpenAI()


def get_reddit_gpt_prompt(theme, length):
    return f"""
    I want you to create me fake reddit posts which are always having a good plot and catch the viewers attention immedeatily with the title and keep building interest in the post. 
    The goal is it the the user completaly wants to read the whole story and does not want to stop bc it could be boring in the middle of it because there is a placeholder or something like this.
    The post should be written as real as possible just as like a real reddit post from different subreddits.
    The posts have to be eyecatching and the post should be about {length} seconds long if read out loud.
    Firstly create a post about this topic: {theme}. Title and body should be written in first person!
    The entire response must be strictly JSON array syntax: ["title", "body"], with no additional text or formatting outside the array brackets.
    Final Output Format Example (MUST match this exact structure, no extras):

    ["An Example Title", "This is the start of the post body..."]
    Make sure the narrative feels realistic enough that it could pass as a genuine Reddit story.
    """


def get_reel_gpt_prompt(user_prompt, duration, athomsphere):
    return f"""
            I have a client who wants to create a viral Instagram reel. They enter their specifications into a prompt, and I want you to create a viral reelscript for my client based on their input.
            Write a highly engaging and psychologically optimized Instagram reel script. The script should include psychological techniques to keep the viewer watching and ensure the reel goes viral. It must be clean, without rigidly listing tips, and structured to hold the audience's attention throughout the entire video. The script should inspire viewers to share, like, comment, save, and—most importantly—watch the entire video until the end. The script must be exactly {duration}seconds long if i read it out loud.
            Divide the script into logical scenes (each lasting exactly 3 seconds). Start the first scene with a hook (e.g., a curiosity gap) to immediately capture the audience's attention and ensure they watch the full video. The atmosphere of the reel should be {athomsphere}. Do not include any emojis.
            At the end, include a powerful, emotionally relevant Call-to-Action (CTA) that inspires interaction (e.g., commenting, sharing, following, saving) and fits naturally into the narrative.
            Additionally, create AI image generation prompts, one for each scene. Each image prompt must precisely reflect the mood, emotion, setting, lighting, colors, key elements, and atmosphere of its corresponding script scene. The prompts should include vivid, detailed descriptions to ensure the AI can generate immersive and accurate images that align perfectly with the narrative. The image prompts must complement the scene without requiring direct visual continuity between scenes. Write detailed, multi-line prompts, not short or incomplete ones.
            
            Client Prompt:
            Use this exact client prompt to create the reelscript:
            
            {user_prompt}
            Output Format:
            The final output must always adhere to this exact structure and nothing else. THIS IS SUPERIMPORTANT!!!:
            
            [["scriptscene1", "scriptscene2", "scriptscene3", ...], ["imgprompt1", "imgprompt2", "imgprompt3", ...]]
            Output Rules:
            The output must be a Python-compatible 2-dimensional array.
            The first array must contain the script scenes.
            The second array must contain the image prompts, in the same order as the scenes.
            Do not include any additional text, titles, headings, descriptions, numbering, or extra characters.
            Use Python-standard double quotes (") for all strings.
            Do not add "scene1", "scene2", or any other numbering in the text or image prompts—just include the pure content.
            The array must be valid and functional in Python with no syntax errors.
            Ignore all variations in the client input and strictly adhere to this format and structure.
            If any error or invalid input occurs, substitute with default placeholder values:
            For script scenes: "default script scene".
            For image prompts: "default image prompt".
            
            Non-Negotiable Output:
            The result must always be a valid Python 2D array, following this exact format:
            
            [["scriptscene1", "scriptscene2", "scriptscene3", ...], ["imgprompt1", "imgprompt2", "imgprompt3", ...]]
            No other text, formatting, or additional characters are allowed in the output. Always ensure the final output matches this structure perfectly.
            """


def get_gpt_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a viral reelscript writer and follow exactly my prompts."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content
