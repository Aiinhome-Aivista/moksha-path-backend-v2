# import random
# import string
# from config import get_db_connection

# def generate_username_suggestions(full_name):
#     """
#     Generates 10 unique username suggestions based on full name.
#     """
#     if not full_name:
#         return []

#     # Clean name: "Riya Roy" -> ["riya", "roy"]
#     parts = "".join(e for e in full_name.lower() if e.isalnum() or e.isspace()).split()
    
#     if not parts: return []
    
#     first = parts[0]
#     last = parts[-1] if len(parts) > 1 else ""
#     base_name = f"{first}{last}"

#     suggestions = set()
    
#     # 1. Generate Smart Combinations
#     suggestions.add(f"{first}{last}")       # riyaroy
#     suggestions.add(f"{last}{first}")       # royriya
#     suggestions.add(f"{first}.{last}")      # riya.roy
#     suggestions.add(f"{first}_{last}")      # riya_roy
#     suggestions.add(f"{first}{random.randint(1, 99)}") # riya01
    
#     # 2. Fill up to 15 candidates with random numbers
#     while len(suggestions) < 15:
#         suffix = random.randint(1, 999)
#         suggestions.add(f"{first}{last}{suffix}")
#         suggestions.add(f"{last}{first}{suffix}")

#     # 3. Filter against Database (Remove taken ones)
#     final_suggestions = []
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         candidates = list(suggestions)
        
#         if candidates:
#             placeholders = ','.join(['%s'] * len(candidates))
#             query = f"SELECT username FROM common.users WHERE username IN ({placeholders})"
#             cur.execute(query, tuple(candidates))
#             taken_usernames = {row[0] for row in cur.fetchall()}
            
#             # Keep only available ones
#             for cand in candidates:
#                 if cand not in taken_usernames:
#                     final_suggestions.append(cand)
#     finally:
#         conn.close()

#     return final_suggestions[:10] # Return top 10 unique available suggestions

import random
import string
from config import get_db_connection
import psycopg2.extras

def generate_username_suggestions(full_name):
    """
    Generates 10 unique username suggestions based on full name.
    """
    if not full_name:
        return []

    # Clean name: "Riya Roy" -> ["riya", "roy"]
    parts = "".join(e for e in full_name.lower() if e.isalnum() or e.isspace()).split()
    
    if not parts: 
        return []
    
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""
    base_name = f"{first}{last}"

    suggestions = set()
    
    # 1. Generate Smart Combinations
    suggestions.add(f"{first}{last}")       # riyaroy
    suggestions.add(f"{last}{first}")       # royriya
    if last:
        suggestions.add(f"{first}.{last}")      # riya.roy
        suggestions.add(f"{first}_{last}")      # riya_roy
    suggestions.add(f"{first}{random.randint(1, 99)}") # riya01
    
    # 2. Fill up to 15 candidates with random numbers
    while len(suggestions) < 15:
        suffix = random.randint(1, 999)
        suggestions.add(f"{first}{last}{suffix}")
        suggestions.add(f"{last}{first}{suffix}")

    # 3. Filter against Database using Stored Procedure
    final_suggestions = []
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        candidates = list(suggestions)
        
        if candidates:
            # Call the Stored Procedure and pass the candidates as a PostgreSQL Array
            cur.execute("""
                CALL common.sp_available_usernames(
                    %s, NULL, NULL, NULL
                )
            """, (candidates,))
            
            result = cur.fetchone()
            
            if result and result['p_status'] == 'success':
                # The SP returns a list of available usernames
                available_usernames = result['p_available_usernames'] or []
                final_suggestions = available_usernames

    except Exception as e:
        print(f"Error filtering usernames: {e}")
    finally:
        if conn:
            conn.close()

    # Return top 10 unique available suggestions
    return final_suggestions[:10]