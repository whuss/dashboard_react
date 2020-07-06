import React from "react";
import { Bar } from "react-chartjs-2";

const BarChart = ({ data }) => {
    const chartData = {
        labels: ["6", "9", "12", "15", "18", "21"],
        datasets: [
            {
                label: "Light shower",
                backgroundColor: "rgba(255,99,132,0.2)",
                borderColor: "rgba(255,99,132,1)",
                borderWidth: 1,
                hoverBackgroundColor: "rgba(255,99,132,0.4)",
                hoverBorderColor: "rgba(255,99,132,1)",
                data: data,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
            display: false,
        },
        scales: {
            xAxes: [
                {
                    gridLines: {
                        drawOnChartArea: false,
                    },
                },
            ],
            yAxes: [
                {
                    ticks: {
                        display: false,
                    },
                    gridLines: {
                        display: false,
                    },
                },
            ],
        },
    };

    return (
        <div style={{ width: "100%", height: "100px", float: "left", position: "relative" }}>
            <Bar data={chartData} options={options} />
        </div>
    );
};

export default BarChart;
