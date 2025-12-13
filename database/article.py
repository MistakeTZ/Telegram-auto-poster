from sqlalchemy.orm import Session

from .orm import Article


def get_existing_articles(session: Session, exist=True, enumerate_=False):
    articles = session.query(Article).filter(Article.is_posted == exist).all()
    if not articles:
        return "отсутствуют"

    articles = [article.theme for article in articles]
    if enumerate_:
        for index, article in enumerate(articles):
            articles[index] = f"{index + 1}. {article}"
    return "\n".join(articles)


def add_article(session: Session, theme, level, article_type):
    article = Article(theme=theme, level=level, article_type=article_type)
    session.add(article)
    return article


def get_article_by_num(session: Session, num: int, exist=False):
    return session.query(Article).filter(Article.is_posted == exist).offset(num).first()
