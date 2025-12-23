interface PriorityBadgeProps {
  score: number;
  demandLevel?: 'high' | 'medium' | 'low';
}

export default function PriorityBadge({ score, demandLevel }: PriorityBadgeProps) {
  const getColor = () => {
    if (score >= 70) return 'bg-gradient-to-r from-red-500 to-red-600 text-white';
    if (score >= 40) return 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-white';
    return 'bg-gradient-to-r from-green-400 to-green-500 text-white';
  };

  const getDemandColor = () => {
    if (demandLevel === 'high') return 'bg-gradient-to-r from-[#005BFF] to-[#0047CC] text-white';
    if (demandLevel === 'medium') return 'bg-gradient-to-r from-[#00D9FF] to-[#005BFF] text-white';
    return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white';
  };

  const getDemandLabel = () => {
    if (demandLevel === 'high') return 'Высокий';
    if (demandLevel === 'medium') return 'Средний';
    return 'Низкий';
  };

  return (
    <div className="flex flex-col items-end space-y-2">
      <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-bold shadow-lg ${getColor()}`}>
        Приоритет: {score.toFixed(0)}
      </span>
      {demandLevel && (
        <span className={`inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold shadow-md ${getDemandColor()}`}>
          Спрос: {getDemandLabel()}
        </span>
      )}
    </div>
  );
}
