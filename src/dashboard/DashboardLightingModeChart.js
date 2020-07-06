import React from "react";
import { Line } from "react-chartjs-2";

const LightingModeChart = ({ automaticColor, monitorColor, paperColor, dataAutomatic, dataMonitor, dataPaper }) => {
    const data = {
        labels: ["6", "9", "12", "15", "18", "21"],
        datasets: [
            {
                label: "Automatic",
                fill: false,
                lineTension: 0.5,
                borderColor: automaticColor,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: monitorColor,
                pointHoverBorderColor: monitorColor,
                pointHoverBorderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 20,
                data: dataAutomatic,
            },
            {
                label: "Monitor",
                fill: false,
                lineTension: 0.5,
                borderColor: monitorColor,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: monitorColor,
                pointHoverBorderColor: monitorColor,
                pointHoverBorderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 20,
                data: dataMonitor,
            },
            {
                label: "Paper",
                fill: false,
                lineTension: 0.5,
                borderColor: paperColor,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: paperColor,
                pointHoverBorderColor: paperColor,
                pointHoverBorderWidth: 2,
                pointRadius: 0,
                pointHitRadius: 20,
                data: dataPaper,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
            position: 'right',
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
        <div style={{width: "100%", height: "24%", float: "left", position: "relative"}}>
            <Line data={data} options={options} />
        </div>
    );
};

export default LightingModeChart;