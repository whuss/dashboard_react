import React from "react";
import { Line } from "react-chartjs-2";
import { LoadingAnimation } from "../framework/Toolbar";
import useDataApi from "../framework/Fetch";

const GazeChart = ({ monitorColor, paperColor, dataMonitor, dataPaper }) => {
    const data = {
        labels: ["6", "9", "12", "15", "18", "21"],
        datasets: [
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
        legend: {
            position: 'right',
        },
    };

    return (
        <Line data={data} options={options} />
    );
};

const Plot = () => {
    const [{ isLoading, isError, data }] = useDataApi("/backend/chart_data", {});

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError}>
            <GazeChart monitorColor="red" paperColor="blue"
                            dataMonitor={data.monitor}
                            dataPaper={data.paper}
                        />
        </LoadingAnimation>
    );
};


export default Plot;
