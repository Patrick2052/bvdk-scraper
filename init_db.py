from core.db import Base, engine


if __name__ == "__main__":
    print("initializing Database models")

    from models import *
    Base.metadata.create_all(bind=engine)

    print("Init Done")
