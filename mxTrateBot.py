<<<<<<< HEAD
from datetime import datetime
from csv import DictReader, DictWriter
from facebook_scraper import get_posts
from requests import get
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

TOKEN = "6314433730:AAH4hg92Q7VnA24pXCNuZyS7o3G2kX6QCQQ"
FIELDNAMES = ["name", "latest_post_time", "latest_post_url"]
=======
from facebook_scraper import get_posts
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
import scraper
import databaseManager


TOKEN = "6314433730:AAH4hg92Q7VnA24pXCNuZyS7o3G2kX6QCQQ"
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
GROUP_ID = -4058684648
MY_ID = 6274617049
LOGIN = ""  # insert email of the scraping facebook account
PASSWORD = ""  # insert password of the scraping facebook account

# conv handler constants
<<<<<<< HEAD
ARE_YOU_SURE_ADD, SITE_CHECK = range(2)
ARE_YOU_SURE_DEL = 1

list_of_sites = []


def main():
    global list_of_sites
    list_of_sites = load_sites()

    application = Application.builder().token(TOKEN).build()
    conv_addsite_handler = ConversationHandler(
        entry_points=[CommandHandler("addsite", add_site)],
        states={
            ARE_YOU_SURE_ADD: [MessageHandler(filters.TEXT & (~filters.COMMAND), are_you_sure_add)],
            SITE_CHECK: [MessageHandler(filters.Regex("^(Ano)$"), site_check),
                         MessageHandler(filters.Regex("^(Ne)$"), add_site)]
=======
ARE_YOU_SURE_ADD, SITE_CHECK, ARE_YOU_SURE_DEL, CONFIRMATION = range(4)
site_to_add: str = ""
remove_site_index: int or None = None
database = databaseManager.database


#
def main():
    application = Application.builder().token(TOKEN).build()
    conv_addsite_handler = ConversationHandler(
        entry_points=[CommandHandler("addsite", conv_add)],
        states={
            ARE_YOU_SURE_ADD: [MessageHandler(filters.TEXT & (~filters.COMMAND), are_you_sure_add)],
            SITE_CHECK: [MessageHandler(filters.Regex("^(Ano)$"), site_check),
                         MessageHandler(filters.Regex("^(Ne)$"), conv_add)]
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
        },
        fallbacks=[CommandHandler("stop", exit_conv)],
    )

    conv_delsite_handler = ConversationHandler(
<<<<<<< HEAD
        entry_points=[CommandHandler("deletesite", del_site)],
        states={
            ARE_YOU_SURE_DEL: [MessageHandler(filters.TEXT & (~filters.COMMAND), are_you_sure_del)]
=======
        entry_points=[CommandHandler("deletesite", conv_del)],
        states={
            ARE_YOU_SURE_DEL: [MessageHandler(filters.TEXT & (~filters.COMMAND), are_you_sure_del)],
            CONFIRMATION: [MessageHandler(filters.Regex("^(Ano)$"), confirm_del),
                           MessageHandler(filters.Regex("^(Ne)$"), conv_del)]
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
        },
        fallbacks=[CommandHandler("stop", exit_conv)],
    )

    application.add_handler(conv_addsite_handler)
    application.add_handler(conv_delsite_handler)

    application.run_polling()
<<<<<<< HEAD
=======

>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
    # new_posts = find_new_posts(sites[0]["name"], sites[0]["latest_post_time"])
    # new_posts = find_new_posts("groups/jsmezbrna", '2023-05-17 15:14:29')
    # update_database(sites, new_posts[0])
    # send_message(6274617049, sites[0]["latest_post_url"], TOKEN)


<<<<<<< HEAD
async def del_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global list_of_sites
    sites = list_of_sites.copy()
    sites_menu = ""
=======
async def conv_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sites = database.sites
    sites_menu = ""
    if not sites:
        scraper.send_msg("Seznam sledovaných stránek je prázdný. Pro přidání stránky použijte příkaz /addsite.")
        return ConversationHandler.END
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
    for i, site in enumerate(sites):
        index = i + 1
        name = site["name"]
        sites_menu += f"{index}. {name}\n"
<<<<<<< HEAD
    await context.bot.send_message(text=
        f"Kterou stránku chcete odebrat?\n{sites_menu}",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
    )

    return ARE_YOU_SURE_DEL


async def add_site(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        text="Prosím zadejte validní název stránky.\n"
        "(https://www.facebook.com/<název_stránky>)",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
    )

    return ARE_YOU_SURE_ADD


site_to_del = None


async def are_you_sure_del(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    print("yep")
    """Prompts the user with a Yes / No keyboard"""
    global site_to_del, list_of_sites
    site_to_del = int(update.message.text) - 1
    keyboard = [["Ano", "Ne"]]
    name = list_of_sites[site_to_del]["name"]
    await context.bot.send_message(
        text=f"Jste si jistý, že chcete odebrat tuto stránku?\nhttps://www.facebook.com/{name}\n"
        "(Ano / Ne)",
=======
    await context.bot.send_message(
        text=f"Kterou stránku chcete odebrat?\n{sites_menu}",
        chat_id=GROUP_ID,
        disable_web_page_preview=True
    )
    return ARE_YOU_SURE_DEL


async def conv_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        text="Prosím zadejte validní název stránky.\n(https://www.facebook.com/<název_stránky>)",
        chat_id=GROUP_ID,
        disable_web_page_preview=True
    )
    return ARE_YOU_SURE_ADD


def is_integer(value: str) -> bool:
    """Returns True if value is integer"""
    try:
        int(value)
    except ValueError:
        return False
    return True


async def are_you_sure_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompts the user with a Yes / No keyboard"""
    global remove_site_index
    try:
        remove_site_index = int(update.message.text) - 1
    except:
        scraper.send_msg("Špatná hodnota. Zadejte číslo v rozmezí 1 až " + str(len(database.sites)))
        return await conv_del(update)

    if remove_site_index < 0 or len(database.sites) - 1 < remove_site_index:
        scraper.send_msg("Špatná hodnota. Zadejte číslo v rozmezí 1 až " + str(len(database.sites)))
        return await conv_del(update, context)

    keyboard = [["Ano", "Ne"]]
    name = database.sites[remove_site_index]["name"]
    await context.bot.send_message(
        text=f"Jste si jistý, že chcete odebrat tuto stránku?\nhttps://www.facebook.com/{name}\n(Ano / Ne)",
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Ano / Ne?",
        ),
    )
<<<<<<< HEAD
    return SITE_CHECK


site_to_add = ""
=======
    return CONFIRMATION


>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
async def are_you_sure_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompts the user with a Yes / No keyboard"""
    global site_to_add
    site_to_add = update.message.text
    keyboard = [["Ano", "Ne"]]
<<<<<<< HEAD
    await context.bot.send_message(text=
        f"Jste si jistý, že chcete přidat tuto stránku?\nhttps://www.facebook.com/{site_to_add}\n"
        "(Ano / Ne)",
=======
    await context.bot.send_message(
        text=f"Jste si jistý, že chcete přidat tuto stránku?\nhttps://www.facebook.com/{site_to_add}\n(Ano / Ne)",
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Ano / Ne?",
        ),
    )
<<<<<<< HEAD
    return SITE_CHECK


async def site_check(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Checks if site_to_add is a valid facebook page"""
    await context.bot.send_message(
        text="Ověřování...",
        chat_id=GROUP_ID,
    )
    print(site_to_add)
    found = False
    for post in get_posts(
        site_to_add,
        pages=1,
        credentials=(LOGIN, PASSWORD),
    ):
        found = True
        break
    if found:
        await context.bot.send_message(
            text="Stránka úspěšně přidána!",
            chat_id=GROUP_ID,
        )
        # TODO: Přidat stránku do databáze
        # add_site(site_to_add)
    else:
        await context.bot.send_message(
            text="CHYBA OVĚŘENÍ",
            chat_id=GROUP_ID,
        )
    return ConversationHandler.END
=======
    site_to_add = site_to_add.lower()
    return SITE_CHECK


async def confirm_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirms if the user wants to delete chosen site"""
    assert remove_site_index is not None
    name = database.sites[remove_site_index]["name"]
    database.remove_site(name)
    scraper.send_msg("Stránka byla odebrána!")
    return ConversationHandler.END


async def site_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Checks if site_to_add is a valid facebook page"""
    scraper.send_msg("Ověřování...")
    if site_to_add in database.sites:
        scraper.send_msg("Stránka se již sleduje.")
        return await conv_add(update, context)

    found = False
    for _ in get_posts(site_to_add, pages=1, credentials=("fbscraping@seznam.cz", "facebook1234")):
        found = True
        break
    if found:
        posts = scraper.search(site_to_add, None)
        newest_post = posts[0]
        database.add_site(newest_post)
        scraper.send_msg("Stránka úspěšně přidána!")
        return ConversationHandler.END

    else:
        scraper.send_msg("CHYBA OVĚŘENÍ")
        return await conv_add(update, context)
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)


async def exit_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
<<<<<<< HEAD
    await context.bot.send_message(text=
        "Příkaz zrušen.",
        chat_id=GROUP_ID,
    )
    return ConversationHandler.END


def load_sites() -> list:
    sites = []
    with open("sites.csv", "r") as file:
        reader = DictReader(file)
        for row in reader:
            sites.append(row)
    return sites


# TODO: Add another parameter "type" which can be group / page
#       if it is a page posts_searched should be 2, else 5
def find_new_posts(site_name: str, time: str) -> list:
    """Looks through the five most recent posts and returns the newly posted ones.
    The newest post is always at index 0.
    """
    old_post_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    posts = []
    posts_searched = 5
    # Searches from the newest to the oldest
    for post in get_posts(
        site_name,
        pages=1,
        credentials=(LOGIN, PASSWORD),
    ):
        posts.append(post)
        if len(posts) == posts_searched:
            break
    newest_post_time = old_post_time
    newly_posted_indexes = []
    sorted_new_posts = []
    new_index = -1
    for i, post in enumerate(posts):
        time = post["time"]
        if time > old_post_time:
            newly_posted_indexes.append(i)
            if time > newest_post_time:
                newest_post_time = time
                new_index = i
    if len(newly_posted_indexes) == 0:
        return []
    sorted_new_posts.append(
        {
            "name": site_name,
            "latest_post_time": str(posts[new_index]["time"]),
            "latest_post_url": posts[new_index]["post_url"],
        }
    )
    for i in newly_posted_indexes:
        if i == new_index:
            continue
        tmp = {
            "name": site_name,
            "latest_post_time": str(posts[i]["time"]),
            "latest_post_url": posts[i]["post_url"],
        }
        sorted_new_posts.append(tmp)
    return sorted_new_posts


def update_database(data: list, new_row: dict) -> None:
    found = False
    for i, row in enumerate(data):
        if new_row["name"] == row["name"]:
            data[i] = new_row
            found = True
    if not found:
        data.append(new_row)
    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)


def send_message(id: int, message: str, usr_token: str):
    url = f"https://api.telegram.org/bot{usr_token}/sendMessage?chat_id={id}&text={message}"
    get(url).json()  # requests


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(update.effective_chat.id)
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


# TODO: Try to make a deep link with users or get UserIDS and save them in list
# TODO: Ask about additional functionality and get the site list
# TODO: Add commands for adding and deleting new sites

if __name__ == "__main__":
    main()

=======
    scraper.send_msg("Příkaz zrušen.")
    return ConversationHandler.END


if __name__ == '__main__':
    main()
>>>>>>> ed7c3d8 (Finalizing new integration of database manager.)
