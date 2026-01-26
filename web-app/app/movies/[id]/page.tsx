import { query } from '@/utils/db';
import { Star, Calendar, Globe, Sparkles, TrendingUp } from 'lucide-react';
import ReviewTrendChart from '@/components/ReviewTrendChart';
import TrendBadge from '@/components/TrendBadge';

export const revalidate = 0;

async function getMovie(id: string) {
    const result = await query('SELECT * FROM movies WHERE tmdb_id = $1 LIMIT 1', [id]);
    return result.rows[0];
}

async function getReviews(title: string) {
    try {
        const result = await query(
            `SELECT r.*, rev.name as reviewer_name, rev.source as reviewer_source
         FROM reviews r
         JOIN reviewers rev ON r.reviewer_id = rev.id
         WHERE r.movie_title = $1`,
            [title]
        );
        return result.rows || [];
    } catch {
        // reviews table may not exist yet
        return [];
    }
}

async function getMovieTrend(movieId: string) {
    try {
        const result = await query(
            `SELECT * FROM movie_trends WHERE movie_id = $1 LIMIT 1`,
            [movieId]
        );
        return result.rows[0];
    } catch {
        return null;
    }
}

async function getRatingSnapshots(movieId: string) {
    try {
        // Use daily_review_snapshots for proper time-series data
        // Supports both hourly and daily snapshots via snapshot_time
        const result = await query(
            `SELECT
                snapshot_time,
                snapshot_date,
                total_reviews,
                critic_score,
                audience_score,
                new_reviews_today,
                review_velocity,
                score_change
             FROM daily_review_snapshots
             WHERE movie_id = $1
             ORDER BY snapshot_time ASC`,
            [movieId]
        );
        return result.rows || [];
    } catch {
        return [];
    }
}

export default async function MoviePage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    const movie = await getMovie(id);

    if (!movie) {
        return <div className="text-white text-center py-24">Movie not found</div>;
    }

    const reviews = await getReviews(movie.title);
    const trend = await getMovieTrend(movie.id);
    const snapshots = await getRatingSnapshots(movie.id);

    return (
        <main className="min-h-screen bg-black text-white">
            {/* Backdrop Header */}
            <div className="relative h-[50vh] w-full">
                <div className="absolute inset-0">
                    {movie.backdrop_url && (
                        <img
                            src={movie.backdrop_url}
                            alt={movie.title}
                            className="h-full w-full object-cover opacity-50"
                        />
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent"></div>
                </div>

                <div className="absolute bottom-0 left-0 w-full p-8 md:p-12">
                    <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-8 items-end">
                        {/* Poster */}
                        {movie.poster_url && (
                            <div className="hidden md:block w-48 shrink-0 rounded-lg overflow-hidden shadow-2xl skew-y-1 transform border-2 border-white/10">
                                <img
                                    src={movie.poster_url}
                                    alt={movie.title}
                                />
                            </div>
                        )}

                        <div className="flex-1 space-y-4">
                            <div className="flex items-center gap-2 text-sm text-indigo-400 font-mono tracking-wider">
                                {movie.regions?.[0] && (
                                    <span className="bg-indigo-900/50 px-2 py-1 rounded border border-indigo-500/30 flex items-center gap-1">
                                        <Globe size={12} /> {movie.regions[0]}
                                    </span>
                                )}
                                {movie.release_date && (
                                    <span className="bg-purple-900/50 px-2 py-1 rounded border border-purple-500/30 flex items-center gap-1">
                                        <Calendar size={12} /> {new Date(movie.release_date).toLocaleDateString()}
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-4 flex-wrap">
                                <h1 className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                                    {movie.title}
                                </h1>
                                {trend && (
                                    <TrendBadge
                                        status={trend.trend_status || 'stable'}
                                        confidence={trend.trend_confidence || 0}
                                    />
                                )}
                            </div>

                            <p className="text-lg text-gray-300 max-w-2xl leading-relaxed">
                                {movie.overview}
                            </p>

                            {(movie.vote_average || movie.vote_count) && (
                                <div className="flex items-center gap-6 pt-2">
                                    {movie.vote_average && (
                                        <div className="flex items-center gap-2 text-yellow-400">
                                            <Star className="fill-current h-6 w-6" />
                                            <span className="text-2xl font-bold">{movie.vote_average.toFixed(1)}</span>
                                            <span className="text-sm text-gray-500">TMDB</span>
                                        </div>
                                    )}
                                    {movie.vote_count && (
                                        <div className="text-sm text-gray-500">
                                            {movie.vote_count} votes
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-12 grid grid-cols-1 lg:grid-cols-3 gap-12">
                {/* Main Content: AI Summary */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 border border-white/5 relative overflow-hidden group">
                        <div className="absolute -right-10 -top-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all"></div>

                        <div className="flex items-center gap-3 mb-6">
                            <Sparkles className="text-indigo-400 h-6 w-6" />
                            <h2 className="text-2xl font-bold text-white">AI Audience Intelligence</h2>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="bg-green-950/30 p-6 rounded-xl border border-green-500/10">
                                <h3 className="text-green-400 font-bold mb-3 uppercase text-sm tracking-wider">The Positives</h3>
                                <p className="text-gray-300 leading-relaxed text-sm">
                                    {movie.ai_summary_positive || "Generating insights..."}
                                </p>
                            </div>

                            <div className="bg-red-950/30 p-6 rounded-xl border border-red-500/10">
                                <h3 className="text-red-400 font-bold mb-3 uppercase text-sm tracking-wider">The Negatives</h3>
                                <p className="text-gray-300 leading-relaxed text-sm">
                                    {movie.ai_summary_negative || "Generating insights..."}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Rating Trends Chart */}
                    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 border border-white/5">
                        <div className="flex items-center gap-3 mb-6">
                            <TrendingUp className="text-blue-400 h-6 w-6" />
                            <h2 className="text-2xl font-bold text-white">Rating Trends Over Time</h2>
                            {trend && (
                                <span className="text-sm text-gray-500">
                                    Growth rate: {((trend.review_growth_rate || 0) * 100).toFixed(1)}%
                                </span>
                            )}
                        </div>
                        <ReviewTrendChart
                            snapshots={snapshots.map((s: any) => ({
                                snapshot_date: s.snapshot_date,
                                total_reviews: Number(s.total_reviews) || 0,
                                new_reviews_today: Number(s.new_reviews_today) || 0,
                                critic_score: Number(s.critic_score) || 0,
                                audience_score: Number(s.audience_score) || 0,
                                review_velocity: Number(s.review_velocity) || 0,
                                score_change: Number(s.score_change) || 0
                            }))}
                            anomalyDates={trend?.spike_date ? [trend.spike_date] : []}
                        />
                    </div>

                    {/* Reviews List */}
                    <div>
                        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                            Regional Reviews <span className="text-sm font-normal text-gray-500">({reviews.length})</span>
                        </h2>
                        <div className="space-y-4">
                            {reviews.length === 0 ? (
                                <div className="text-gray-500 italic">No reviews collected yet.</div>
                            ) : (
                                reviews.map((review: any) => (
                                    <div key={review.id} className="bg-gray-900 p-6 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-bold text-gray-200">{review.reviewer_name || "Unknown Critic"}</span>
                                            <span className={`text-sm px-2 py-0.5 rounded ${review.rating === 'Fresh' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                                                {review.rating}
                                            </span>
                                        </div>
                                        <p className="text-gray-400 text-sm leading-relaxed">"{review.content}"</p>
                                        <div className="mt-2 flex justify-between items-center text-xs text-gray-600">
                                            <span>{review.reviewer_source}</span>
                                            <span>{review.review_date}</span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Sidebar: Metadata or Recs (Placeholder) */}
                <div className="space-y-6">
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h3 className="text-lg font-bold mb-4 text-gray-300">Film Details</h3>
                        <ul className="space-y-3 text-sm">
                            <li className="flex justify-between">
                                <span className="text-gray-500">ID</span>
                                <span className="font-mono text-gray-300">{movie.tmdb_id}</span>
                            </li>
                            {movie.language && (
                                <li className="flex justify-between">
                                    <span className="text-gray-500">Language</span>
                                    <span className="text-gray-300 uppercase">{movie.language}</span>
                                </li>
                            )}
                            {movie.popularity && (
                                <li className="flex justify-between">
                                    <span className="text-gray-500">Popularity</span>
                                    <span className="text-gray-300">{movie.popularity.toFixed(0)}</span>
                                </li>
                            )}
                            {trend && (
                                <>
                                    <li className="flex justify-between">
                                        <span className="text-gray-500">Trend Status</span>
                                        <span className="text-gray-300 capitalize">{trend.trend_status?.replace('_', ' ') || 'Unknown'}</span>
                                    </li>
                                    <li className="flex justify-between">
                                        <span className="text-gray-500">Avg Daily Reviews</span>
                                        <span className="text-gray-300">{(trend.avg_daily_reviews || 0).toFixed(1)}</span>
                                    </li>
                                </>
                            )}
                        </ul>
                    </div>
                </div>
            </div>
        </main>
    );
}
