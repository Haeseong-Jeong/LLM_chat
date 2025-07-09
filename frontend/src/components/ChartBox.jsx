import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Chart } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

function ChartBox({ data }) {
  const labels = data.map((item) => item.Date);
  const chartData = {
    labels,
    datasets: [
      {
        type: "bar",
        label: "입고량",
        data: data.map((item) => Number(item["입고량"])),
        backgroundColor: "#6EC5FF",
      },
      {
        type: "bar",
        label: "출고량",
        data: data.map((item) => Number(item["출고량"])),
        backgroundColor: "#1F77B4",
      },
      {
        type: "line",
        label: "입출고차이",
        data: data.map((item) => Number(item["입출고차이"])),
        borderColor: "orange",
        backgroundColor: "orange",
        tension: 0.3,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "white" },
        grid: { color: "#333" },
      },
      y: {
        ticks: { color: "white" },
        grid: { color: "#333" },
      },
    },
  };

  return (
    <div style={{ marginTop: 20, background: "#1E1E1E", padding: 20, borderRadius: 10 }}>
      <h4 style={{ color: "white", marginBottom: 10 }}>📊 입출고량 시각화</h4>
      <Chart type="bar" data={chartData} options={chartOptions} />
    </div>
  );
}

export default ChartBox;
