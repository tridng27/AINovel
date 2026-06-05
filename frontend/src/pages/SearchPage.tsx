import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import NovelCard, { type NovelCardData } from "../components/NovelCard";
import { GENRES } from "../constants/genres";
import { novelService, type Novel, type NovelSort } from "../services/novels";
import { searchService, type SearchHit } from "../services/search";
import "./search.css";

function novelToCard(n: Novel): NovelCardData {
  return { slug: n.slug, title: n.title, cover: n.cover_image_url, rating: n.rating_avg, views: n.view_count, status: n.status };
}
function hitToCard(h: SearchHit): NovelCardData {
  return { slug: h.slug, title: h.title, cover: h.cover_url, rating: h.rating_avg, views: h.view_count };
}

export default function SearchPage() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get("q") ?? "");
  const [cards, setCards] = useState<NovelCardData[]>([]);
  const [loading, setLoading] = useState(false);

  const genre = params.get("genre") ? Number(params.get("genre")) : undefined;
  const sort = (params.get("sort") as NovelSort) || "view_count";

  useEffect(() => {
    const query = params.get("q") ?? "";
    setLoading(true);
    const run = query.trim()
      ? searchService.novels(query, { genre_id: genre }).then((r) => r.data.hits.map(hitToCard))
      : novelService.list({ genre_id: genre, sort, page_size: 40 }).then((r) => r.data.items.map(novelToCard));
    run
      .then(setCards)
      .catch(() => setCards([]))
      .finally(() => setLoading(false));
  }, [params]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const next = new URLSearchParams(params);
    if (q.trim()) next.set("q", q.trim());
    else next.delete("q");
    setParams(next);
  };

  const setGenre = (id?: number) => {
    const next = new URLSearchParams(params);
    if (id) next.set("genre", String(id));
    else next.delete("genre");
    setParams(next);
  };

  const setSort = (s: NovelSort) => {
    const next = new URLSearchParams(params);
    next.set("sort", s);
    setParams(next);
  };

  return (
    <div className="search-page">
      <form className="search-bar" onSubmit={submit}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Tìm truyện, tác giả, thể loại..."
        />
        <button type="submit">Tìm</button>
      </form>

      <div className="search-filters">
        <button className={!genre ? "chip active" : "chip"} onClick={() => setGenre(undefined)}>
          Tất cả
        </button>
        {GENRES.map((g) => (
          <button key={g.id} className={genre === g.id ? "chip active" : "chip"} onClick={() => setGenre(g.id)}>
            {g.name}
          </button>
        ))}
      </div>

      {!params.get("q") && (
        <div className="search-sort">
          Sắp xếp:
          <button className={sort === "view_count" ? "active" : ""} onClick={() => setSort("view_count")}>
            Phổ biến
          </button>
          <button className={sort === "rating_avg" ? "active" : ""} onClick={() => setSort("rating_avg")}>
            Đánh giá
          </button>
          <button className={sort === "updated_at" ? "active" : ""} onClick={() => setSort("updated_at")}>
            Mới nhất
          </button>
        </div>
      )}

      {loading ? (
        <p className="muted">Đang tải…</p>
      ) : cards.length === 0 ? (
        <p className="muted">Không tìm thấy truyện nào.</p>
      ) : (
        <div className="search-grid">
          {cards.map((c) => (
            <NovelCard key={c.slug} {...c} />
          ))}
        </div>
      )}
    </div>
  );
}
