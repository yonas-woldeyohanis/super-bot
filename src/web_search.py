from duckduckgo_search import DDGS

def search_web(query):
    """Searches the web and returns the top 3 results"""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return None
        
        formatted_results = ""
        for res in results:
            formatted_results += f"• {res['title']}: {res['body']}\nLink: {res['href']}\n\n"
            
        return formatted_results
    except Exception as e:
        return f"Error searching web: {str(e)}"