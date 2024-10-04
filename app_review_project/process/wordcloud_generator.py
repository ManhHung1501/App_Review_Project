from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(reviews):
    # Combine all reviews into a single string
    text = " ".join(review['review'] for review in reviews)
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Display the generated word cloud image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # No axes for a cleaner look
    plt.show()
