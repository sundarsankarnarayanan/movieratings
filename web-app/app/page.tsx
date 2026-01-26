import { query } from '@/utils/db';
import Link from 'next/link';
import { TrendingUp, Clock } from 'lucide-react';

export const revalidate = 0;

async function getTrendingMovies() {
  const result = await query(`
    SELECT DISTINCT ON (m.id)
      m.id, m.tmdb_id, m.title, m.release_date, m.poster_url,
      rs.rating_value as current_rating,
      rs.source,
      (
        SELECT rating_value FROM movie_platform.rating_snapshots rs2
        WHERE rs2.movie_id = m.id 
        AND rs2.source = rs.source
        AND rs2.snapshot_time < NOW() - INTERVAL '24 hours'
        ORDER BY rs2.snapshot_time DESC
        LIMIT 1
      ) as rating_24h_ago
    FROM movie_platform.movies m
    JOIN movie_platform.rating_snapshots rs ON m.id = rs.movie_id
    WHERE rs.snapshot_time > NOW() - INTERVAL '7 days'
    AND rs.rating_type = 'tomatometer'
    ORDER BY m.id, rs.snapshot_time DESC
    LIMIT 20
  `);

  return result.rows.map(row => ({
    ...row,
    rating_change: row.rating_24h_ago ? row.current_rating - row.rating_24h_ago : 0
  }));
}

async function getRecentMovies() {
  const result = await query(`
    SELECT * FROM movie_platform.movies
    ORDER BY release_date DESC
    LIMIT 12
  `);
  return result.rows;
}

export default async function Home() {
  const trendingMovies = await getTrendingMovies();
  const recentMovies = await getRecentMovies();

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-900/50 to-purple-900/50 py-16">
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Real-Time Movie Trends
          </h1>
          <p className="mt-4 text-xl text-gray-300 max-w-2xl">
            Track rating changes across global review platforms in real-time
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 space-y-16">
        {/* Trending Section */}
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

        {/* Recent Releases */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Clock className="text-indigo-500 h-8 w-8" />
            <h2 className="text-3xl font-bold text-white">
              Latest Releases
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {recentMovies.map((movie) => (
              <Link
                key={movie.id}
                href={`/movies/${movie.tmdb_id}`}
                className="group block"
              >
                <div className="aspect-[2/3] w-full overflow-hidden rounded-lg bg-gray-800">
                  {movie.poster_url && (
                    <img
                      src={movie.poster_url}
                      alt={movie.title}
                      className="h-full w-full object-cover group-hover:scale-110 transition-transform"
                    />
                  )}
                </div>
                <p className="mt-2 text-sm font-medium text-white truncate">{movie.title}</p>
                <p className="text-xs text-gray-500">
                  {movie.release_date instanceof Date
                    ? movie.release_date.toLocaleDateString()
                    : String(movie.release_date)}
                </p>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
