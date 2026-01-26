'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { format } from 'date-fns';

interface DailySnapshot {
    snapshot_time?: string;
    snapshot_date: string;
    total_reviews: number;
    new_reviews_today: number;
    critic_score: number;
    audience_score: number;
    review_velocity: number;
    score_change: number;
}

interface ReviewTrendChartProps {
    snapshots: DailySnapshot[];
    anomalyDates?: string[];
}

export default function ReviewTrendChart({ snapshots, anomalyDates = [] }: ReviewTrendChartProps) {
    if (!snapshots || snapshots.length === 0) {
        return (
            <div className="text-center py-12 text-gray-500">
                <p>No trend data available yet</p>
                <p className="text-sm mt-2">Check back after a few days of monitoring</p>
            </div>
        );
    }

    // Detect if we have hourly data (multiple snapshots on same day)
    const dates = snapshots.map(s => s.snapshot_date);
    const uniqueDates = new Set(dates);
    const isHourly = snapshots.length > uniqueDates.size;

    // Format data for chart
    const chartData = snapshots.map(s => {
        const timestamp = s.snapshot_time ? new Date(s.snapshot_time) : new Date(s.snapshot_date);
        const dateLabel = isHourly
            ? format(timestamp, 'MMM d HH:mm')
            : format(timestamp, 'MMM d');

        return {
            date: dateLabel,
            fullDate: s.snapshot_time || s.snapshot_date,
            reviews: s.new_reviews_today,
            totalReviews: s.total_reviews,
            criticScore: s.critic_score,
            audienceScore: s.audience_score,
            velocity: s.review_velocity,
            scoreChange: s.score_change
        };
    });

    // Custom tooltip
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            const isAnomaly = anomalyDates.includes(data.fullDate);

            return (
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-xl">
                    <p className="text-white font-bold mb-2">{data.date}</p>
                    {isAnomaly && (
                        <p className="text-yellow-400 text-sm mb-2">⚠️ Unusual Activity</p>
                    )}
                    <div className="space-y-1 text-sm">
                        <p className="text-blue-400">New Reviews: {data.reviews}</p>
                        <p className="text-gray-400">Total: {data.totalReviews}</p>
                        <p className="text-purple-400">Velocity: {data.velocity?.toFixed(1)}/day</p>
                        {data.criticScore && (
                            <p className="text-green-400">Critic Score: {data.criticScore}%</p>
                        )}
                        {data.scoreChange !== 0 && (
                            <p className={data.scoreChange > 0 ? 'text-green-400' : 'text-red-400'}>
                                Change: {data.scoreChange > 0 ? '+' : ''}{data.scoreChange?.toFixed(1)}%
                            </p>
                        )}
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full">
            <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                        dataKey="date"
                        stroke="#9CA3AF"
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis
                        yAxisId="left"
                        stroke="#9CA3AF"
                        style={{ fontSize: '12px' }}
                        label={{ value: 'Reviews', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
                    />
                    <YAxis
                        yAxisId="right"
                        orientation="right"
                        stroke="#9CA3AF"
                        style={{ fontSize: '12px' }}
                        domain={[0, 100]}
                        label={{ value: 'Score %', angle: 90, position: 'insideRight', fill: '#9CA3AF' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />

                    {/* Anomaly reference lines */}
                    {anomalyDates.map(date => {
                        const dataPoint = chartData.find(d => d.fullDate === date);
                        if (dataPoint) {
                            return (
                                <ReferenceLine
                                    key={date}
                                    x={dataPoint.date}
                                    stroke="#FBBF24"
                                    strokeDasharray="3 3"
                                    label={{ value: '⚠️', position: 'top', fill: '#FBBF24' }}
                                />
                            );
                        }
                        return null;
                    })}

                    <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="reviews"
                        stroke="#3B82F6"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        name="New Reviews"
                    />
                    <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="criticScore"
                        stroke="#10B981"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        name="Critic Score"
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
