from notion_client import Client
import yaml

# read yml file
config = yaml.safe_load(open("config.yml", "r"))
notion = Client(auth=config["notion"]["token"])

def fetch_event(db_type: str = "general") -> list:
    response = notion.databases.query(
        database_id=config["notion"]["database"][db_type],
    )

    event_list = []

    for page in response["results"]:
        properties = page["properties"]

        # Extract name
        name = properties["Name"]["title"][0]["plain_text"] if properties["Name"]["title"] else "無標題"

        # Extract date
        date_prop = properties["Date"]["date"]
        start_time = date_prop["start"] if date_prop else None
        end_time = date_prop["end"] if date_prop and date_prop["end"] else None

        # Extract assigned users
        assign_prop = properties["Assign"]["people"]
        assigned_users = [person["name"] for person in assign_prop]

        event = {
            "name": name,
            "start": start_time,
            "end": end_time,
            "assigned": assigned_users
        }

        event_list.append(event)

    return event_list

if __name__ == "__main__":
    events = fetch_event("secret")
    for event in events:
        print(f"🗓️ 活動名稱: {event['name']}")
        print(f"   起始時間: {event['start']}")
        print(f"   結束時間: {event['end']}")
        print(f"   負責人員: {', '.join(event['assigned']) if event['assigned'] else '無'}")
        print("-" * 40)

