# Telegram Auto-Poster for Cooking Recipes

Telegram Auto-Poster is a sophisticated Python-based bot that automates the creation and publication of cooking recipes to a Telegram channel. It leverages AI models like GPT-4o for generating unique recipe ideas and text, and DALL-E 3 for creating appealing images. The bot is designed to run on a schedule, ensuring a consistent flow of content for your audience.

## Features

- **AI-Powered Content Generation**: Utilizes OpenAI's GPT models to write unique and engaging cooking recipes, including titles, descriptions, ingredients, and step-by-step instructions.
- **Automatic Image Creation**: Generates high-quality, appetizing images for each recipe using DALL-E 3.
-**Scheduled Posting**: Posts content at pre-configured times, allowing for different meal themes (breakfast, lunch, dinner) throughout the day.
- **Theme-Based Generation**: Selects a recipe theme (e.g., "Breakfast", "Desserts") based on the time of day and configurable probabilities to ensure content variety.
- **Duplicate Prevention**: Keeps track of previously posted recipes in an SQLite database to avoid repetition.
- **Intelligent Formatting**: Automatically formats posts with HTML for Telegram, including bold and italic text, and dynamically adds relevant hashtags.
- **Persistent Storage**: Saves all posted articles, including text, image URLs, and Telegram post links, in a local SQLite database and a `recipes.json` file.

## How It Works

The bot operates through a scheduled workflow:

1.  **Scheduling**: The `main.py` script starts a scheduler that runs continuously. It calculates the time until the next scheduled post based on your environment settings.
2.  **Theme Selection**: When it's time to post, the bot selects a meal theme (e.g., breakfast, lunch, dinner) based on the posting hour.
3.  **Recipe Idea Generation**: The bot queries the GPT model to come up with a new recipe idea for the selected theme, ensuring it hasn't been posted before by checking the local database.
4.  **Content Writing**: Once a unique recipe is chosen, a second request is sent to GPT to write the full post, complete with a title, engaging description, ingredients list, instructions, and relevant hashtags. The text is formatted using HTML for Telegram.
5.  **Image Generation**: The generated recipe text is used as a prompt for the DALL-E 3 model to create a matching, appetizing image.
6.  **Posting**: The final text and image are sent to the designated Telegram channel.
7.  **Data Logging**: After a successful post, the bot saves the article's details, including the Telegram message ID and photo ID, to the SQLite database and updates a `recipes.json` file.

## Setup and Installation

### Prerequisites

-   Python 3.12+

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/mistaketz/telegram-auto-poster.git
    cd telegram-auto-poster
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure your environment variables by creating a `.env` file from the example:
    ```bash
    cp example.env .env
    ```

4.  Edit the `.env` file with your credentials and settings:

    -   `api_key`: Your OpenAI API key.
    -   `token`: Your Telegram Bot token.
    -   `channel`: Your Telegram channel username (e.g., `@mychannel`) or ID.
    -   `article_end`: A custom signature or text to append to every post. Use `\n` for new lines.
    -   `breakfast`: Comma-separated list of hours (24-hour format) to post breakfast recipes (e.g., `8,9`).
    -   `launch`: Comma-separated list of hours for lunch recipes (e.g., `12,13,14`).
    -   `dinner`: Comma-separated list of hours for dinner recipes (e.g., `18,19,20`).

## Usage

### Running the Scheduler

To start the bot and have it post automatically according to the schedule in your `.env` file, run:

```bash
python main.py
```

The console will log the time of the next scheduled post.

### Posting Immediately

To test the bot and post a single recipe immediately, run the script with the `send_now` argument:

```bash
python main.py send_now
```

## Project Structure

```
├── agents/             # Clients for interacting with OpenAI APIs (GPT, DALL-E)
├── database/           # SQLAlchemy ORM, database setup, and seed data
├── expressions/        # Prompt templates for the AI models
├── generators/         # Core logic for generation, scheduling, and sending
├── telegram/           # Modules for Telegram formatting and posting
├── utils/              # Utility functions for images, scraping, and file handling
├── main.py             # Main entry point for the application
├── example.env         # Example environment configuration file
└── requirements.txt    # Project dependencies