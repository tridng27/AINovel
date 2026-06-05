import { ReactNode } from "react";
import { Link } from "react-router-dom";

interface CarouselProps {
  title: string;
  moreLink?: string;
  children: ReactNode;
  empty?: boolean;
}

export default function Carousel({ title, moreLink, children, empty }: CarouselProps) {
  return (
    <section className="carousel">
      <div className="carousel-head">
        <h2>{title}</h2>
        {moreLink && (
          <Link to={moreLink} className="carousel-more">
            Xem tất cả →
          </Link>
        )}
      </div>
      {empty ? (
        <p className="carousel-empty">Chưa có truyện.</p>
      ) : (
        <div className="carousel-row">{children}</div>
      )}
    </section>
  );
}
