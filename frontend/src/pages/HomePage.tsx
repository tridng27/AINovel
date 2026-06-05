import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Carousel from "../components/Carousel";
import NovelCard, { type NovelCardData } from "../components/NovelCard";
import { novelService, type Novel } from "../services/novels";
import "./home.css";

function toCard(n: Novel): NovelCardData {
  return { slug: n.slug, title: n.title, cover: n.cover_image_url, rating: n.rating_avg, views: n.view_count, status: n.status };
}

interface Section {
  key: string;
  title: string;
  moreLink: string;
  novels: Novel[];
}

export default function HomePage() {
  const [hero, setHero] = useState<Novel | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [popular, recent, topRated, fantasy, romance, scifi] = await Promise.all([
        novelService.list({ sort: "view_count", page_size: 12 }),
        novelService.list({ sort: "updated_at", page_size: 12 }),
        novelService.list({ sort: "rating_avg", page_size: 12 }),
        novelService.list({ genre_id: 1, page_size: 12 }),
        novelService.list({ genre_id: 2, page_size: 12 }),
        novelService.list({ genre_id: 3, page_size: 12 }),
      ]);
      setHero(topRated.data.items[0] ?? popular.data.items[0] ?? null);
      setSections([
        { key: "popular", title: "🔥 Phổ biến nhất", moreLink: "/search?sort=view_count", novels: popular.data.items },
        { key: "recent", title: "🆕 Mới cập nhật", moreLink: "/search?sort=updated_at", novels: recent.data.items },
        { key: "top", title: "⭐ Đánh giá cao", moreLink: "/search?sort=rating_avg", novels: topRated.data.items },
        { key: "fantasy", title: "Huyền huyễn", moreLink: "/search?genre=1", novels: fantasy.data.items },
        { key: "romance", title: "Ngôn tình", moreLink: "/search?genre=2", novels: romance.data.items },
        { key: "scifi", title: "Khoa học viễn tưởng", moreLink: "/search?genre=3", novels: scifi.data.items },
      ]);
      setLoading(false);
    }
    load().catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="home2"><p className="muted">Đang tải…</p></div>;

  return (
    <div className="home2">
      {hero && (
        <section
          className="hero2"
          style={hero.cover_image_url ? { backgroundImage: `url(${hero.cover_image_url})` } : undefined}
        >
          <div className="hero2-overlay">
            <span className="hero2-tag">Nổi bật</span>
            <h1>{hero.title}</h1>
            {hero.synopsis && <p>{hero.synopsis}</p>}
            <div className="hero2-meta">
              ⭐ {hero.rating_avg.toFixed(1)} · 👁 {hero.view_count.toLocaleString()} · {hero.chapter_count} chương
            </div>
            <Link to={`/novels/${hero.slug}`} className="btn-primary">
              Đọc ngay
            </Link>
          </div>
        </section>
      )}

      {sections.map((s) => (
        <Carousel key={s.key} title={s.title} moreLink={s.moreLink} empty={s.novels.length === 0}>
          {s.novels.map((n) => (
            <NovelCard key={n.id} {...toCard(n)} />
          ))}
        </Carousel>
      ))}
    </div>
  );
}
