from datetime import datetime
from csv import DictReader, DictWriter
from facebook_scraper import get_posts
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

import scraper

TOKEN = ""  # insert telegram group token
FIELDNAMES = ["name", "latest_post_time", "latest_post_url"]
GROUP_ID = -4058684648
MY_ID = 6274617049
LOGIN = ""  # insert email of the scraping facebook account
PASSWORD = ""  # insert password of the scraping facebook account

# conv handler constants
ARE_YOU_SURE_ADD, SITE_CHECK, ARE_YOU_SURE_DEL, CONFIRMATION = range(4)

site_to_add: str = ""
site_to_del: int or str = None
list_of_sites: list[dict] or list[None] = []


# TODO: udělat další thread na notifikace
def main():
    global list_of_sites
    list_of_sites = load_sites()
    application = Application.builder().token(TOKEN).build()
    conv_addsite_handler = ConversationHandler(
        entry_points=[CommandHandler("addsite", conv_add)],
        states={
            ARE_YOU_SURE_ADD: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), are_you_sure_add
                )
            ],
            SITE_CHECK: [
                MessageHandler(filters.Regex("^(Ano)$"), site_check),
                MessageHandler(filters.Regex("^(Ne)$"), conv_add),
            ],
        },
        fallbacks=[CommandHandler("stop", exit_conv)],
    )

    conv_delsite_handler = ConversationHandler(
        entry_points=[CommandHandler("deletesite", conv_del)],
        states={
            ARE_YOU_SURE_DEL: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), are_you_sure_del
                )
            ],
            CONFIRMATION: [
                MessageHandler(filters.Regex("^(Ano)$"), confirm_del),
                MessageHandler(filters.Regex("^(Ne)$"), conv_del),
            ],
        },
        fallbacks=[CommandHandler("stop", exit_conv)],
    )

    application.add_handler(conv_addsite_handler)
    application.add_handler(conv_delsite_handler)

    application.run_polling()

    # new_posts = find_new_posts(sites[0]["name"], sites[0]["latest_post_time"])
    # new_posts = find_new_posts("groups/jsmezbrna", '2023-05-17 15:14:29')
    # update_database(sites, new_posts[0])
    # send_message(6274617049, sites[0]["latest_post_url"], TOKEN)


async def conv_del(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global list_of_sites
    sites = list_of_sites.copy()
    sites_menu = ""
    if not sites:
        await context.bot.send_message(
            text="Seznam sledovaných stránek je prázdný. Pro přidání stránky použijte příkaz /addsite.",
            chat_id=GROUP_ID,
        )
        return ConversationHandler.END
    for i, site in enumerate(sites):
        index = i + 1
        name = site["name"]
        sites_menu += f"{index}. {name}\n"
    await context.bot.send_message(
        text=f"Kterou stránku chcete odebrat?\n{sites_menu}",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
    )
    return ARE_YOU_SURE_DEL


async def conv_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        text="Prosím zadejte validní název stránky.\n(https://www.facebook.com/<název_stránky>)",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
    )
    return ARE_YOU_SURE_ADD


def is_integer(value: str) -> bool:
    """Returns True if value is integer"""
    try:
        int(value)
    except ValueError:
        return False
    return True


async def are_you_sure_del(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Prompts the user with a Yes / No keyboard"""
    global site_to_del, list_of_sites
    try:
        site_to_del = int(update.message.text) - 1
    except:
        await context.bot.send_message(
            text="Špatná hodnota. Zadejte číslo v rozmezí 1 až "
            + str(len(list_of_sites)),
            chat_id=GROUP_ID,
        )
        return await conv_del(update, context)

    if site_to_del < 0 or len(list_of_sites) - 1 < site_to_del:
        await context.bot.send_message(
            text="Špatná hodnota. Zadejte číslo v rozmezí 1 až "
            + str(len(list_of_sites)),
            chat_id=GROUP_ID,
        )
        return await conv_del(update, context)

    keyboard = [["Ano", "Ne"]]
    name = list_of_sites[site_to_del]["name"]
    await context.bot.send_message(
        text=f"Jste si jistý, že chcete odebrat tuto stránku?\nhttps://www.facebook.com/{name}\n(Ano / Ne)",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Ano / Ne?",
        ),
    )
    return CONFIRMATION


async def are_you_sure_add(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Prompts the user with a Yes / No keyboard"""
    global site_to_add
    site_to_add = update.message.text
    keyboard = [["Ano", "Ne"]]
    await context.bot.send_message(
        text=f"Jste si jistý, že chcete přidat tuto stránku?\nhttps://www.facebook.com/{site_to_add}\n(Ano / Ne)",
        chat_id=GROUP_ID,
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Ano / Ne?",
        ),
    )
    site_to_add = site_to_add.lower()
    return SITE_CHECK


async def confirm_del(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Confirms if user wants to delete the site"""
    assert site_to_del is not None
    delete_site(list_of_sites, list_of_sites[site_to_del])
    await context.bot.send_message(
        text="Stránka byla odebrána!",
        chat_id=GROUP_ID,
    )
    return ConversationHandler.END


def site_in_database(data: list, site_name: str) -> bool:
    for row in data:
        if row["name"] == site_name:
            return True
    return False


async def site_check(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Checks if site_to_add is a valid facebook page"""
    await context.bot.send_message(
        text="Ověřování...",
        chat_id=GROUP_ID,
    )

    global list_of_sites
    if site_in_database(list_of_sites, site_to_add):
        await context.bot.send_message(
            text="Stránka se již sleduje.",
            chat_id=GROUP_ID,
        )
        return await conv_add(update, context)

    found = False
    for _ in get_posts(
        site_to_add,
        pages=1,
        credentials=(LOGIN, PASSWORD),
    ):
        found = True
        break
    if found:
        posts = scraper.search(site_to_add, None)
        add_site(list_of_sites, posts[0])
        await context.bot.send_message(
            text="Stránka úspěšně přidána!",
            chat_id=GROUP_ID,
        )
        return ConversationHandler.END

    else:
        await context.bot.send_message(
            text="CHYBA OVĚŘENÍ",
            chat_id=GROUP_ID,
        )
        return await conv_add(update, context)


async def exit_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await context.bot.send_message(
        text="Příkaz zrušen.",
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


def delete_site(data: list[dict], row: dict) -> None:
    for i, row_data in enumerate(data):
        if row_data["name"] == row["name"]:
            data.pop(i)

    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)


def update_site(data: list[dict], new_row: dict) -> None:
    found = False
    for i, row in enumerate(data):
        if new_row["name"] == row["name"]:
            data[i] = new_row
            found = True

    if not found:
        return

    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)


def add_site(data: list[dict], new_row: dict) -> None:
    data.append(new_row)
    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    main()
