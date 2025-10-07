from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import random, datetime

TOKEN = "8077198127:AAGpgtYdNciKHXvMAhRbvu7XUUFebx89MhE"
ADMIN_ID = 5918407549  # <-- Replace with your Telegram user ID

# --- Menu & Data ---
MENU_ITEMS = {
    "Pizza": "₹199",
    "Burger": "₹149",
    "Pasta": "₹179",
    "Cold Drink": "₹49",
    "Dessert": "₹99",
}

WELCOME_MESSAGES = [
    "🍕 Welcome to *Yash Restaurant!* Your hunger ends here 😋",
    "🍔 Hello foodie! *Yash Restaurant* is cooking happiness for you 🔥",
    "🥗 Welcome back! Let’s roll some taste magic 🌮✨",
]

FUNNY_REPLIES = [
    "🍟 You’re officially a food legend now! 😎",
    "🍕 The chef just smiled — your order made his day! 😂",
    "🍔 Zero calories if you smile while eating! 😉",
    "🍰 You deserve dessert for being awesome! 🎂",
]

FOOD_FACTS = {
    "Pizza": "🍕 Pizza was first made in Naples, Italy!",
    "Burger": "🍔 The first hamburger was made in 1900 in the USA.",
    "Pasta": "🍝 Pasta has over 600 shapes worldwide!",
    "Cold Drink": "🥤 Soft drinks were invented in the 1800s.",
    "Dessert": "🍰 Desserts are the happiest part of any meal!"
}

DAILY_SPECIALS = list(MENU_ITEMS.keys())

# --- Utility Functions ---
def get_daily_special():
    day = datetime.datetime.now().weekday()
    special_item = DAILY_SPECIALS[day % len(DAILY_SPECIALS)]
    discount = random.choice([10, 15, 20])
    return f"🔥 Today's Special: *{special_item}* at {discount}% OFF! 🔥"

def get_random_deal():
    deal_item = random.choice(list(MENU_ITEMS.keys()))
    discount = random.choice([5, 10, 15])
    return f"🎉 Surprise Deal: *{deal_item}* gets {discount}% OFF today! 🎉"

def themed_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "☀️ Good Morning Foodie!"
    elif 12 <= hour < 17:
        return "🌤️ Good Afternoon! Hungry?"
    elif 17 <= hour < 21:
        return "🌇 Good Evening! Time for a snack?"
    else:
        return "🌙 Good Night! Late night cravings?"

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = random.choice(WELCOME_MESSAGES)
    await update.message.reply_text(f"{themed_greeting()}\n{msg}", parse_mode="Markdown")
    await update.message.reply_text(get_daily_special(), parse_mode="Markdown")
    await update.message.reply_text(get_random_deal(), parse_mode="Markdown")
    await update.message.reply_text("Type /menu to explore our tasty dishes 🍽️")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for item, price in MENU_ITEMS.items():
        keyboard.append([InlineKeyboardButton(f"{item} — {price}", callback_data=f"item_{item}")])
    keyboard.append([InlineKeyboardButton("Book a Table 🪑", callback_data="book")])
    keyboard.append([InlineKeyboardButton("Search Menu 🔍", callback_data="search")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍽️ *Yash Restaurant Menu* 🍽️", parse_mode="Markdown", reply_markup=reply_markup)

async def book_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("🪑 Enter your name & time (e.g., `Yash 8PM`) to book a table:", parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text("🪑 Enter your name & time (e.g., `Yash 8PM`) to book a table:", parse_mode="Markdown")

# --- Inline Button Handler ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "book":
        await book_table(update, context)
    elif query.data == "search":
        await query.message.reply_text("🔍 Type the food name to search in menu:")
    elif query.data.startswith("item_"):
        item = query.data.replace("item_", "")
        fact = FOOD_FACTS.get(item, "")
        reply = random.choice(FUNNY_REPLIES)
        await query.edit_message_text(text=f"✅ You chose *{item}*!\n{fact}\n{reply}", parse_mode="Markdown")

# --- Admin Commands ---
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    try:
        item = context.args[0]
        price = context.args[1]
        MENU_ITEMS[item] = price
        FOOD_FACTS[item] = f"Fun fact about {item}!"
        await update.message.reply_text(f"✅ Added *{item} — {price}*", parse_mode="Markdown")
    except:
        await update.message.reply_text("Usage: /additem <ItemName> <Price>")

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    try:
        item = context.args[0]
        if item in MENU_ITEMS:
            del MENU_ITEMS[item]
            del FOOD_FACTS[item]
            await update.message.reply_text(f"✅ Removed *{item}*", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Item not found")
    except:
        await update.message.reply_text("Usage: /removeitem <ItemName>")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized!")
        return
    message = " ".join(context.args)
    # Normally here you save all user IDs and loop to send message
    await update.message.reply_text(f"✅ Broadcast sent: {message}")

# --- Message Handler ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Table booking
    if any(x in text for x in ["pm", "am"]):
        reply = random.choice(FUNNY_REPLIES)
        await update.message.reply_text(f"✅ Table booked for *{text}*! {reply}", parse_mode="Markdown")
    
    # Search menu
    elif text in [i.lower() for i in MENU_ITEMS.keys()]:
        price = MENU_ITEMS[text.capitalize()]
        fact = FOOD_FACTS.get(text.capitalize(), "")
        await update.message.reply_text(f"🍽️ *{text.capitalize()}* — {price}\n{fact}", parse_mode="Markdown")
    
    # AI-like Q&A
    elif "time" in text:
        await update.message.reply_text("⏰ We are open from 10 AM to 10 PM daily!")
    elif "menu" in text:
        await menu(update, context)
    elif "special" in text:
        await update.message.reply_text(get_daily_special(), parse_mode="Markdown")
    else:
        await update.message.reply_text("🤔 Didn’t get that! Try /menu or /book")

# --- Bot Setup ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("book", book_table))
app.add_handler(CommandHandler("additem", add_item))
app.add_handler(CommandHandler("removeitem", remove_item))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("🤖 Yash Restaurant Crazy Bot is LIVE 🍕🔥")
app.run_polling()
