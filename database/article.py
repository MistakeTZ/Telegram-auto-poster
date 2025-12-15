from sqlalchemy.orm import Session

from .orm import Article


def get_existing_articles(session: Session, exist=True, enumerate_=False, maximum=10):
    articles = session.query(Article).filter(Article.is_posted == exist).all()
    if not articles:
        return "отсутствуют"

    articles = [article.name for article in articles][-maximum:]
    if enumerate_:
        for index, article in enumerate(articles):
            articles[index] = f"{index + 1}. {article}"
    return "\n".join(articles)


def add_article(session: Session, **kwargs):
    article = Article(**kwargs, is_posted=False)
    session.add(article)
    session.commit()
    return article
