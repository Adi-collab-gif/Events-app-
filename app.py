import streamlit as st
from openai import OpenAI
import requests
from io import BytesIO
from PIL import Image
import base64

def generate_social_media_posts(event_details, api_key):
    """Generate social media posts for LinkedIn, Twitter, and WhatsApp using OpenAI."""
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Create social media posts for LinkedIn, Twitter, and WhatsApp about the following event:
        
        {event_details}
        
        The tone should be professional but with a touch of humor - nothing over the top.
        
        For each platform, follow these guidelines:
        
        1. LinkedIn: A professional post that showcases the event's value, around 1-2 paragraphs with appropriate hashtags.
        
        2. Twitter: A concise, engaging post under 280 characters that captures attention, with relevant hashtags.
        
        3. WhatsApp: A friendly, informative message that people would want to share with friends or colleagues.
        
        Format the response clearly with headers for each platform.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error generating posts: {str(e)}")
        return None

def generate_event_image(event_details, api_key):
    """Generate an image for the event using DALL-E 3."""
    try:
        client = OpenAI(api_key=api_key)
        
        # Create a prompt for the image
        image_prompt = f"""
        Create a professional, visually appealing promotional image for this event:
        
        {event_details}
        
        The image should be suitable for social media posts across LinkedIn, Twitter, and WhatsApp.
        It should be modern, clean, and engaging with elements that represent the event's theme.
        """
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            style="vivid"
        )
        
        image_url = response.data[0].url
        
        # Get the image from the URL
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        
        return img, image_url
    
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None, None

def get_image_download_link(img, filename, text):
    """Generate a download link for the image."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}.png">{text}</a>'
    return href

def main():
    st.set_page_config(page_title="Social Media Post Generator", layout="wide")
    
    st.title("📱 Social Media Post Generator")
    st.write("Create professional posts for LinkedIn, Twitter, and WhatsApp about your event with matching images.")
    
    # API key input in sidebar
    st.sidebar.title("Configuration")
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    st.sidebar.markdown("""
    ### About this app
    This app generates social media posts and promotional images for your events using OpenAI's GPT-4o and DALL-E 3 models.
    
    You need to provide your own API key to use the app. Your key is not stored and is only used for generating content.
    
    ### How to use
    1. Enter your OpenAI API key in the sidebar
    2. Describe your event in detail in the text area
    3. Click 'Generate Content'
    4. Copy the generated posts for each platform
    5. Download the event image
    """)
    
    # Main area for event details input
    event_details = st.text_area(
        "Event Details:", 
        height=200,
        placeholder="Describe your event in detail. Include information like:\n- Event name\n- Date and time\n- Location\n- Purpose\n- Key speakers or attractions\n- Target audience\n- Any special features"
    )
    
    generate_btn = st.button("Generate Content")
    
    if generate_btn:
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not event_details or len(event_details.strip()) < 10:
            st.error("Please provide more details about your event.")
        else:
            # Generate content
            col1, col2 = st.columns([3, 2])
            
            with st.spinner("Generating social media posts..."):
                posts = generate_social_media_posts(event_details, api_key)
                
            with st.spinner("Creating promotional image..."):
                image, image_url = generate_event_image(event_details, api_key)
            
            if posts and image:
                st.success("Content generated successfully!")
                
                with col1:
                    st.subheader("Social Media Posts")
                    st.markdown(posts)
                    
                    # Add copy buttons for each platform
                    sections = posts.split('LinkedIn:')
                    if len(sections) > 1:
                        linkedin_text = sections[1].split('Twitter:')[0].strip()
                        twitter_text = sections[1].split('Twitter:')[1].split('WhatsApp:')[0].strip()
                        whatsapp_text = sections[1].split('WhatsApp:')[1].strip()
                        
                        st.subheader("Copy Individual Posts")
                        post_tabs = st.tabs(["LinkedIn", "Twitter", "WhatsApp"])
                        
                        with post_tabs[0]:
                            st.text_area("LinkedIn Post", linkedin_text, height=150)
                        
                        with post_tabs[1]:
                            st.text_area("Twitter Post", twitter_text, height=100)
                        
                        with post_tabs[2]:
                            st.text_area("WhatsApp Post", whatsapp_text, height=150)
                    
                with col2:
                    st.subheader("Promotional Image")
                    st.image(image, use_column_width=True)
                    
                    # Generate download link
                    download_filename = "event_promo_image"
                    st.markdown(get_image_download_link(image, download_filename, "Download Image"), unsafe_allow_html=True)
                    
                    with st.expander("View the image prompt"):
                        st.write(f"""
                        Create a professional, visually appealing promotional image for this event:
                        
                        {event_details}
                        
                        The image should be suitable for social media posts across LinkedIn, Twitter, and WhatsApp.
                        It should be modern, clean, and engaging with elements that represent the event's theme.
                        """)

if __name__ == "__main__":
    main()