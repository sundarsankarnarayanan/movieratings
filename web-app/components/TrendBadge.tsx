interface TrendBadgeProps {
    status: 'trending_up' | 'trending_down' | 'sleeper_hit' | 'stable';
    confidence?: number;
    showLabel?: boolean;
}

export default function TrendBadge({ status, confidence = 0, showLabel = true }: TrendBadgeProps) {
    const configs = {
        trending_up: {
            icon: '🔥',
            label: 'Trending Up',
            bgColor: 'bg-green-500/20',
            textColor: 'text-green-400',
            borderColor: 'border-green-500/50'
        },
        trending_down: {
            icon: '📉',
            label: 'Trending Down',
            bgColor: 'bg-red-500/20',
            textColor: 'text-red-400',
            borderColor: 'border-red-500/50'
        },
        sleeper_hit: {
            icon: '💎',
            label: 'Sleeper Hit',
            bgColor: 'bg-purple-500/20',
            textColor: 'text-purple-400',
            borderColor: 'border-purple-500/50'
        },
        stable: {
            icon: '➡️',
            label: 'Stable',
            bgColor: 'bg-gray-500/20',
            textColor: 'text-gray-400',
            borderColor: 'border-gray-500/50'
        }
    };

    const config = configs[status] || configs.stable;

    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${config.bgColor} ${config.borderColor}`}>
            <span className="text-lg">{config.icon}</span>
            {showLabel && (
                <span className={`text-sm font-medium ${config.textColor}`}>
                    {config.label}
                </span>
            )}
            {confidence > 0 && (
                <span className="text-xs text-gray-500">
                    ({Math.round(confidence * 100)}%)
                </span>
            )}
        </div>
    );
}
