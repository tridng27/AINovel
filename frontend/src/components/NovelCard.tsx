import { Link } from "react-router-dom";

export interface NovelCardData {
  slug: string;
  title: string;
  cover: string | null;
  rating: number | null;
  views: number;
  status?: string;
}

function formatViews(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

export default function NovelCard({ slug, title, cover, rating, views, status }: NovelCardData) {
  return (
    <Link to={`/novels/${slug}`} className="ncard">
      <div className="ncard-cover">
        {cover ? (
          <img src={cover} alt={title} loading="lazy" />
        ) : (
          <div className="ncard-noimg">{title.slice(0, 1)}</div>
        )}
        {status === "completed" && <span className="ncard-badge">Hoàn thành</span>}
      </div>
      <div className="ncard-title">{title}</div>
      <div className="ncard-meta">
        <span>⭐ {rating != null ? rating.toFixed(1) : "—"}</span>
        <span>👁 {formatViews(views)}</span>
      </div>
    </Link>
  );
}
