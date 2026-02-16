import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsChartsProps {
  analytics: any;
}

const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ analytics }) => {
  // Category breakdown data
  const categoryData = analytics.category_breakdown ? 
    Object.entries(analytics.category_breakdown).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      cases: value
    })) : [];

  // Mock monthly data for trend
  const monthlyData = [
    { month: 'Aug', resolved: 8, savings: 12000 },
    { month: 'Sep', resolved: 10, savings: 15000 },
    { month: 'Oct', resolved: 11, savings: 16500 },
    { month: 'Nov', resolved: 12, savings: 18500 },
  ];

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Cases by Category */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Cases by Category</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="cases" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Performance */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Cases Resolved (Trend)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="resolved" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Category Distribution Pie */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Category Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={categoryData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="cases"
            >
              {categoryData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Money Saved Trend */}
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Money Saved (Trend)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
            <Line type="monotone" dataKey="savings" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default AnalyticsCharts;