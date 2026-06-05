// Khớp với dữ liệu seed trong DB (bảng genres). IDs cố định theo thứ tự seed.
export interface Genre {
  id: number;
  name: string;
  slug: string;
}

export const GENRES: Genre[] = [
  { id: 1, name: "Huyền huyễn", slug: "fantasy" },
  { id: 2, name: "Ngôn tình", slug: "romance" },
  { id: 3, name: "Khoa học viễn tưởng", slug: "sci-fi" },
  { id: 4, name: "Tiên hiệp", slug: "xianxia" },
  { id: 5, name: "Kiếm hiệp", slug: "wuxia" },
  { id: 6, name: "Đô thị", slug: "urban" },
  { id: 7, name: "Trinh thám", slug: "mystery" },
  { id: 8, name: "Kinh dị", slug: "horror" },
];
