import Link from 'next/link';
import { Star } from 'lucide-react';

interface Movie {
    tmdb_id: number;
    title: string;
    release_date: string;
    poster_path: string;
    vote_average: number;
    region: string;
    ai_summary_positive?: string;
}

export default function MovieCard({ movie }: { movie: Movie }) {
    const imageUrl = movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : 'https://via.placeholder.com/500x750?text=No+Poster';

    return (
        <Link href={`/movies/${movie.tmdb_id}`} className="group relative block overflow-hidden rounded-xl bg-gray-900 transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-indigo-500/20">
            <div className="aspect-[2/3] w-full overflow-hidden">
                <img
                    src={imageUrl}
                    alt={movie.title}
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent opacity-60"></div>
            </div>

            <div className="absolute bottom-0 p-4 w-full">
                <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">{movie.region}</span>
                    <div className="flex items-center gap-1 text-yellow-400">
                        <Star className="h-3 w-3 fill-current" />
                        <span className="text-sm font-bold">{movie.vote_average.toFixed(1)}</span>
                    </div>
                </div>
                <h3 className="text-lg font-bold text-white leading-tight truncate">{movie.title}</h3>
                <p className="text-xs text-gray-400 mt-1">{movie.release_date}</p>

                {movie.ai_summary_positive && (
                    <div className="mt-2 text-[10px] text-green-300 line-clamp-2 bg-green-900/30 p-1 rounded backdrop-blur-sm border border-green-500/20">
                        ✨ {movie.ai_summary_positive}
                    </div>
                )}
            </div>
        </Link>
    );
}
