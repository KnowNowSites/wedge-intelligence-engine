"""
Product Hunt Scraper - Extracts new product launches with demand signals.
Uses official Product Hunt GraphQL API (requires PRODUCTHUNT_API_TOKEN in .env).
"""

from datetime import datetime, timedelta
import os
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("producthunt_scraper")


@safe_scraper_execution("producthunt_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def producthunt_scraper() -> list[dict]:
    """
    Scrape Product Hunt for new launches (last 90 days) using GraphQL API.
    
    Requires: PRODUCTHUNT_API_TOKEN environment variable
    
    Returns:
        List of dicts with: product_name, tagline, upvotes, comments, category_tags, 
        launch_date, url, hunter_username
    """
    logger.info("Starting Product Hunt scraper...")
    
    api_token = os.getenv("PRODUCTHUNT_API_TOKEN", "").strip()
    if not api_token:
        logger.warning("PRODUCTHUNT_API_TOKEN not set. Skipping Product Hunt scraper.")
        return []
    
    try:
        import requests
    except ImportError:
        logger.error("requests not installed. Run: pip install requests")
        return []
    
    results = []
    
    try:
        # Product Hunt GraphQL endpoint
        url = "https://api.producthunt.com/v2/api/graphql"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        
        # GraphQL query for products from last 90 days
        query = """
        {
            posts(first: 50, after: "", order: NEWEST) {
                edges {
                    node {
                        id
                        name
                        tagline
                        votesCount
                        commentsCount
                        url
                        hunter {
                            username
                        }
                        createdAt
                        productTags {
                            tag {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        payload = {"query": query}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            logger.error(f"Product Hunt API error: {data['errors']}")
            return []
        
        posts = data.get("data", {}).get("posts", {}).get("edges", [])
        logger.info(f"Fetched {len(posts)} products from Product Hunt")
        
        for post_edge in posts:
            try:
                node = post_edge.get("node", {})
                
                # Extract product data
                product_name = node.get("name", "")
                tagline = node.get("tagline", "")
                upvotes = node.get("votesCount", 0)
                comments = node.get("commentsCount", 0)
                url = node.get("url", "")
                hunter_username = node.get("hunter", {}).get("username", "")
                created_at = node.get("createdAt", "")
                
                # Extract category tags
                tags = node.get("productTags", [])
                category_tags = ",".join([t.get("tag", {}).get("name", "") for t in tags])
                
                # Check if product is from last 90 days
                try:
                    launch_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if (datetime.now(launch_date.tzinfo) - launch_date).days > 90:
                        continue
                except:
                    launch_date = datetime.now()
                
                # Flag for wedge signal: high upvote-to-comment ratio in niche categories
                upvote_to_comment_ratio = upvotes / max(comments, 1)
                
                results.append({
                    "product_name": product_name,
                    "tagline": tagline,
                    "upvotes": upvotes,
                    "comments": comments,
                    "category_tags": category_tags,
                    "launch_date": launch_date,
                    "url": url,
                    "hunter_username": hunter_username,
                    "upvote_to_comment_ratio": upvote_to_comment_ratio,
                })
            
            except Exception as e:
                logger.debug(f"Error parsing Product Hunt post: {e}")
                continue
        
        randomized_delay(2, 4)
    
    except Exception as e:
        logger.error(f"Product Hunt scraper error: {e}")
        return []
    
    logger.info(f"Product Hunt scraper completed: {len(results)} products found")
    return results


def save_producthunt_launches(launches: list[dict]) -> int:
    """Save Product Hunt launches to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for launch in launches:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO producthunt_launches 
                (product_name, tagline, upvotes, comments, category_tags, launch_date, url, hunter_username, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                launch.get("product_name"),
                launch.get("tagline"),
                launch.get("upvotes", 0),
                launch.get("comments", 0),
                launch.get("category_tags"),
                launch.get("launch_date"),
                launch.get("url"),
                launch.get("hunter_username"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save Product Hunt launch: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(launches)} Product Hunt launches to database")
    return saved


if __name__ == "__main__":
    launches = producthunt_scraper()
    save_producthunt_launches(launches)
