from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# ==========================
# DATABASE
# ==========================

DATABASE_URL = "sqlite:///blogs.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

class Base(DeclarativeBase):
    pass

class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(5000))
    author: Mapped[str] = mapped_column(String(100))

Base.metadata.create_all(bind=engine)

# ==========================
# PYDANTIC SCHEMAS
# ==========================

class BlogCreate(BaseModel):
    title: str
    content: str
    author: str

class BlogResponse(BlogCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================
# FASTAPI APP
# ==========================

app = FastAPI(title="Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# CREATE BLOG
# ==========================

@app.post("/blogs", response_model=BlogResponse)
def create_blog(blog: BlogCreate):

    with Session(engine) as session:
        new_blog = Blog(
            title=blog.title,
            content=blog.content,
            author=blog.author
        )

        session.add(new_blog)
        session.commit()
        session.refresh(new_blog)

        return new_blog

# ==========================
# GET ALL BLOGS
# ==========================

@app.get("/blogs", response_model=list[BlogResponse])
def get_blogs():

    with Session(engine) as session:
        blogs = session.query(Blog).all()
        return blogs

# ==========================
# GET SINGLE BLOG
# ==========================

@app.get("/blogs/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: int):

    with Session(engine) as session:
        blog = session.get(Blog, blog_id)

        if not blog:
            raise HTTPException(
                status_code=404,
                detail="Blog not found"
            )

        return blog

# ==========================
# UPDATE BLOG
# ==========================

@app.put("/blogs/{blog_id}", response_model=BlogResponse)
def update_blog(blog_id: int, updated_blog: BlogCreate):

    with Session(engine) as session:

        blog = session.get(Blog, blog_id)

        if not blog:
            raise HTTPException(
                status_code=404,
                detail="Blog not found"
            )

        blog.title = updated_blog.title
        blog.content = updated_blog.content
        blog.author = updated_blog.author

        session.commit()
        session.refresh(blog)

        return blog

# ==========================
# DELETE BLOG
# ==========================

@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int):

    with Session(engine) as session:

        blog = session.get(Blog, blog_id)

        if not blog:
            raise HTTPException(
                status_code=404,
                detail="Blog not found"
            )

        session.delete(blog)
        session.commit()

        return {
            "message": "Blog deleted successfully"
        }