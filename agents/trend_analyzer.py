"""
Agent 4: Trend Analyzer
Analyzes daily review snapshots and classifies movie trends
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, timedelta
import statistics

load_dotenv()

class TrendAnalyzer:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD")
        )
        self.conn.autocommit = True
        
        with self.conn.cursor() as cur:
            cur.execute("SET search_path TO movie_platform;")
    
    def get_active_movies(self, days=30):
        """Get movies released in the last N days"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT * FROM movies 
                WHERE release_date > NOW() - INTERVAL '%s days'
                ORDER BY release_date DESC;
            """
            cur.execute(query, (days,))
            return cur.fetchall()
    
    def get_daily_snapshots(self, movie_id, days=7):
        """Get daily snapshots for a movie"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT * FROM daily_review_snapshots
                WHERE movie_id = %s
                AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY snapshot_date ASC;
            """
            cur.execute(query, (movie_id, days))
            return cur.fetchall()
    
    def calculate_trend_slope(self, snapshots):
        """Calculate linear regression slope for review velocity"""
        if len(snapshots) < 2:
            return 0.0
        
        # Use review velocity as y-axis
        x_values = list(range(len(snapshots)))
        y_values = [s['review_velocity'] or 0 for s in snapshots]
        
        # Simple linear regression
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def detect_sleeper_hit(self, snapshots):
        """Detect if movie is a sleeper hit (slow start, then spike)"""
        if len(snapshots) < 5:
            return False, 0.0
        
        # Split into early and late periods
        mid_point = len(snapshots) // 2
        early_snapshots = snapshots[:mid_point]
        late_snapshots = snapshots[mid_point:]
        
        # Calculate average velocity for each period
        early_avg = sum(s['review_velocity'] or 0 for s in early_snapshots) / len(early_snapshots)
        late_avg = sum(s['review_velocity'] or 0 for s in late_snapshots) / len(late_snapshots)
        
        # Sleeper hit if late period is 3x+ higher than early
        if early_avg > 0 and late_avg / early_avg >= 3.0:
            # Also check for score improvement
            early_scores = [s['critic_score'] for s in early_snapshots if s['critic_score']]
            late_scores = [s['critic_score'] for s in late_snapshots if s['critic_score']]
            
            if early_scores and late_scores:
                score_improvement = (sum(late_scores) / len(late_scores)) - (sum(early_scores) / len(early_scores))
                if score_improvement >= 5.0:  # At least 5% improvement
                    return True, late_avg / early_avg
        
        return False, 0.0
    
    def detect_anomalies(self, snapshots):
        """Detect suspicious spikes in review activity"""
        if len(snapshots) < 3:
            return False, None, 0.0
        
        # Calculate standard deviation of new_reviews_today
        review_counts = [s['new_reviews_today'] or 0 for s in snapshots]
        
        if len(review_counts) < 2:
            return False, None, 0.0
        
        mean = statistics.mean(review_counts)
        stdev = statistics.stdev(review_counts) if len(review_counts) > 1 else 0
        
        if stdev == 0:
            return False, None, 0.0
        
        # Check for spikes > 5 standard deviations
        for snapshot in snapshots:
            new_reviews = snapshot['new_reviews_today'] or 0
            if new_reviews > mean + (5 * stdev):
                magnitude = (new_reviews - mean) / stdev
                return True, snapshot['snapshot_date'], magnitude
        
        return False, None, 0.0
    
    def classify_trend(self, movie_id):
        """Classify movie trend status"""
        snapshots = self.get_daily_snapshots(movie_id, days=7)
        
        if not snapshots:
            return {
                'trend_status': 'stable',
                'trend_confidence': 0.0,
                'avg_daily_reviews': 0.0,
                'review_growth_rate': 0.0,
                'score_momentum': 0.0,
                'has_suspicious_activity': False,
                'spike_detected': False,
                'spike_date': None,
                'spike_magnitude': None
            }
        
        # Calculate metrics
        slope = self.calculate_trend_slope(snapshots)
        is_sleeper, sleeper_ratio = self.detect_sleeper_hit(snapshots)
        has_spike, spike_date, spike_magnitude = self.detect_anomalies(snapshots)
        
        # Calculate average daily reviews
        avg_daily_reviews = sum(s['new_reviews_today'] or 0 for s in snapshots) / len(snapshots)
        
        # Calculate growth rate (compare first half vs second half)
        mid_point = len(snapshots) // 2
        if mid_point > 0:
            early_avg = sum(s['new_reviews_today'] or 0 for s in snapshots[:mid_point]) / mid_point
            late_avg = sum(s['new_reviews_today'] or 0 for s in snapshots[mid_point:]) / (len(snapshots) - mid_point)
            review_growth_rate = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0.0
        else:
            review_growth_rate = 0.0
        
        # Calculate score momentum (average score change)
        score_changes = [s['score_change'] or 0 for s in snapshots]
        score_momentum = sum(score_changes) / len(score_changes) if score_changes else 0.0
        
        # Classify trend
        if is_sleeper:
            trend_status = 'sleeper_hit'
            confidence = min(sleeper_ratio / 5.0, 1.0)  # Normalize to 0-1
        elif slope > 0.5:
            trend_status = 'trending_up'
            confidence = min(abs(slope) / 2.0, 1.0)
        elif slope < -0.5:
            trend_status = 'trending_down'
            confidence = min(abs(slope) / 2.0, 1.0)
        else:
            trend_status = 'stable'
            confidence = 1.0 - min(abs(slope), 1.0)
        
        return {
            'trend_status': trend_status,
            'trend_confidence': confidence,
            'avg_daily_reviews': avg_daily_reviews,
            'review_growth_rate': review_growth_rate,
            'score_momentum': score_momentum,
            'has_suspicious_activity': has_spike,
            'spike_detected': has_spike,
            'spike_date': spike_date,
            'spike_magnitude': spike_magnitude
        }
    
    def store_trend(self, movie_id, trend_data):
        """Store trend classification in database"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO movie_trends (
                    movie_id, trend_status, trend_confidence,
                    avg_daily_reviews, review_growth_rate, score_momentum,
                    has_suspicious_activity, spike_detected, spike_date, spike_magnitude
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (movie_id) DO UPDATE SET
                    trend_status = EXCLUDED.trend_status,
                    trend_confidence = EXCLUDED.trend_confidence,
                    avg_daily_reviews = EXCLUDED.avg_daily_reviews,
                    review_growth_rate = EXCLUDED.review_growth_rate,
                    score_momentum = EXCLUDED.score_momentum,
                    has_suspicious_activity = EXCLUDED.has_suspicious_activity,
                    spike_detected = EXCLUDED.spike_detected,
                    spike_date = EXCLUDED.spike_date,
                    spike_magnitude = EXCLUDED.spike_magnitude,
                    last_calculated_at = NOW()
                RETURNING *;
            """
            
            cur.execute(query, (
                movie_id,
                trend_data['trend_status'],
                trend_data['trend_confidence'],
                trend_data['avg_daily_reviews'],
                trend_data['review_growth_rate'],
                trend_data['score_momentum'],
                trend_data['has_suspicious_activity'],
                trend_data['spike_detected'],
                trend_data['spike_date'],
                trend_data['spike_magnitude']
            ))
            
            return cur.fetchone()
    
    def analyze_all(self):
        """Analyze trends for all active movies"""
        print("🔍 Analyzing movie trends...")
        
        movies = self.get_active_movies(days=30)
        print(f"Found {len(movies)} active movies")
        
        analyzed_count = 0
        for movie in movies:
            try:
                print(f"\n  Analyzing: {movie['title']}")
                trend_data = self.classify_trend(movie['id'])
                
                stored_trend = self.store_trend(movie['id'], trend_data)
                if stored_trend:
                    status_icon = {
                        'trending_up': '🔥',
                        'trending_down': '📉',
                        'sleeper_hit': '💎',
                        'stable': '➡️'
                    }.get(trend_data['trend_status'], '❓')
                    
                    print(f"    {status_icon} Status: {trend_data['trend_status']}")
                    print(f"    📊 Avg daily reviews: {trend_data['avg_daily_reviews']:.1f}")
                    print(f"    📈 Growth rate: {trend_data['review_growth_rate']:+.1f}%")
                    
                    if trend_data['has_suspicious_activity']:
                        print(f"    ⚠️ Spike detected on {trend_data['spike_date']} ({trend_data['spike_magnitude']:.1f}σ)")
                    
                    analyzed_count += 1
                    
            except Exception as e:
                print(f"    ❌ Error analyzing {movie['title']}: {e}")
        
        print(f"\n✅ Analyzed {analyzed_count} movies")
        self.conn.close()

if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    analyzer.analyze_all()
