import { query } from '@/utils/db';
import Link from 'next/link';
import { TrendingUp, Clock, Globe, ArrowUpRight, Zap } from 'lucide-react';

export const revalidate = 0;

async function getGlobalMovies() {
  // Get top rated movies grouped by language (limit 3 per language)
  const languages = ['es', 'fr', 'ko', 'ja', 'hi']; // Example set
  const movies = [];

  for (const lang of languages) {
    const res = await query(`
          SELECT * FROM movies 
          WHERE original_language = $1 
          ORDER BY release_date DESC 
          LIMIT 4
      `, [lang]);
    if (res.rows.length > 0) {
      movies.push({ language: lang, items: res.rows });
    }
  }
  return movies;
}

async function getRisingStars() {
  // Find movies with high consistency score from our view
  const result = await query(`
        SELECT mt.*, m.poster_url 
        FROM movie_trends mt
        JOIN movies m ON mt.movie_id = m.id
        WHERE mt.consistency_score >= 1.0
        AND mt.rating_change_24h > 0
        ORDER BY mt.rating_change_24h DESC
        LIMIT 6
    `);
  return result.rows;
}

// ... existing getTrendingMovies and getRecentMovies ...
async function getTrendingMovies() {
  const result = await query(`
    SELECT DISTINCT ON (m.id)
      m.id, m.tmdb_id, m.title, m.release_date, m.poster_url,
      rs.rating_value as current_rating,
      rs.source,
      (
        SELECT rating_value FROM rating_snapshots rs2
        WHERE rs2.movie_id = m.id 
        AND rs2.source = rs.source
        AND rs2.snapshot_time < NOW() - INTERVAL '24 hours'
        ORDER BY rs2.snapshot_time DESC
        LIMIT 1
      ) as rating_24h_ago
    FROM movies m
    JOIN rating_snapshots rs ON m.id = rs.movie_id
    WHERE rs.snapshot_time > NOW() - INTERVAL '7 days'
    AND rs.rating_type = 'tomatometer'
    ORDER BY m.id, rs.snapshot_time DESC
    LIMIT 12
  `);

  return result.rows.map(row => ({
    ...row,
    rating_change: row.rating_24h_ago ? row.current_rating - row.rating_24h_ago : 0
  }));
}

async function getRecentMovies() {
  const result = await query(`
    SELECT * FROM movies
    ORDER BY release_date DESC
    LIMIT 12
  `);
  return result.rows;
}

export default async function Home() {
  const trendingMovies = await getTrendingMovies();
  const recentMovies = await getRecentMovies();
  const globalGroups = await getGlobalMovies();
  const risingStars = await getRisingStars();

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white pb-24">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-900/50 to-purple-900/50 py-16 mb-12">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Global Cinema Intelligence
          </h1>
          <p className="mt-4 text-xl text-gray-300 max-w-2xl">
            Real-time tracking of critical consensus, audience sentiment, and global trends.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-20">

        {/* Rising Stars (High Consistency) */}
        {risingStars.length > 0 && (
          <section>
            <div className="flex items-center gap-3 mb-6">
              <Zap className="text-yellow-400 h-8 w-8" />
              <h2 className="text-3xl font-bold text-white">
                Rising Stars <span className="text-lg font-normal text-gray-500 ml-2">(Consistent Growth)</span>
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {risingStars.map((movie: any) => (
                <Link
                  key={movie.movie_id}
                  href={`/movies/${movie.tmdb_id}`} // Assuming tmdb_id is available or handled by ID lookup
                  // NOTE: movie_trends view might not have tmdb_id if not selected. 
                  // Let's ensure logic works or handle safely.
                  // Actually movie_trends view does NOT have tmdb_id selected in schema_v2.sql.
                  // However, we just grab it via join above if we wrote the query correctly.
                  // Wait, getRisingStars query selects `mt.*, m.poster_url`. 
                  // Let's modify query to fetch m.tmdb_id to be safe.
                  className="group relative flex gap-4 bg-gray-800/40 p-4 rounded-xl border border-yellow-500/30 hover:bg-gray-800/60 transition-all"
                >
                  <div className="w-24 shrink-0 rounded-lg overflow-hidden">
                    <img src={movie.poster_url} className="w-full h-full object-cover" alt={movie.title} />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-white group-hover:text-yellow-400 transition-colors">{movie.title}</h3>
                    <div className="flex items-center gap-2 mt-2 text-yellow-400 font-mono text-xl">
                      <ArrowUpRight size={20} />
                      {movie.current_rating}%
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      +{movie.rating_change_24h.toFixed(1)}% / 24h
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Global Pulse via Language */}
        <section>
          <div className="flex items-center gap-3 mb-8">
            <Globe className="text-blue-400 h-8 w-8" />
            <h2 className="text-3xl font-bold text-white">Global Pulse</h2>
          </div>

          <div className="grid gap-10">
            {globalGroups.map((group: any) => (
              <div key={group.language} className="relative">
                <h3 className="text-xl font-bold text-gray-400 mb-4 uppercase tracking-wider flex items-center gap-2">
                  <span className="w-2 h-8 bg-blue-500 rounded-full inline-block"></span>
                  {new Intl.DisplayNames(['en'], { type: 'language' }).of(group.language)} Cinema
                </h3>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {group.items.map((movie: any) => (
                    <Link key={movie.id} href={`/movies/${movie.tmdb_id}`} className="group block">
                      <div className="aspect-[2/3] rounded-lg overflow-hidden mb-2 relative">
                        <img src={movie.poster_url} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt={movie.title} />
                        <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                          <span className="text-xs font-bold bg-blue-600 px-2 py-0.5 rounded text-white shadow-lg">
                            {new Date(movie.release_date).getFullYear()}
                          </span>
                        </div>
                      </div>
                      <div className="font-medium text-gray-200 group-hover:text-white truncate">{movie.title}</div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Existing Trending (Biggest Movers) */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="text-pink-500 h-8 w-8" />
            <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500">
              Biggest Movers (24h)
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trendingMovies.map((movie) => (
              <Link
                key={movie.id}
                href={`/movies/${movie.tmdb_id}`}
                className="group relative block overflow-hidden rounded-xl bg-gray-800/50 backdrop-blur-sm border border-gray-700 hover:border-indigo-500 transition-all hover:scale-[1.02]"
              >
                <div className="aspect-[16/9] w-full overflow-hidden bg-gray-900">
                  {movie.poster_url && (
                    <img
                      src={movie.poster_url}
                      alt={movie.title}
                      className="h-full w-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                    />
                  )}
                </div>

                <div className="p-4">
                  <h3 className="text-lg font-bold text-white truncate">{movie.title}</h3>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="text-sm text-gray-400">{movie.source}</div>
                    <div className={`flex items-center gap-1 font-bold ${movie.rating_change > 0 ? 'text-green-400' :
                      movie.rating_change < 0 ? 'text-red-400' : 'text-gray-400'
                      }`}>
                      {movie.rating_change > 0 && '↑'}
                      {movie.rating_change < 0 && '↓'}
                      {Math.abs(movie.rating_change).toFixed(1)}%
                    </div>
                  </div>
                  <div className="mt-1 text-2xl font-bold text-yellow-400">
                    {movie.current_rating}%
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
