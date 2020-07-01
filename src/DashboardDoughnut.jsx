import React from "react";
import { Doughnut } from "react-chartjs-2";

const data = {
    labels: ["Red", "Green", "Yellow"],
    datasets: [
        {
            data: [300, 50, 100],
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
            hoverBackgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
        },
    ],
};

const DoughnutExample = ({firstLine, secondLine}) => {
    const options = {
        cutoutPercentage: 80,
        legend: {
            display: false,
        },
    };

    return (
        <div style={{width: "100%", height: "100%", float: "left", position: "relative"}}>
            <div style={{width: "100%", height: "40px", position: "absolute", top: "50%", left: 0, marginTop: "-20px", lineHeight: "19px", textAlign: "center", zIndex: 999999999999999}}>
                {firstLine}
                <br />
                {secondLine}
            </div>
            <Doughnut data={data} options={options} />
        </div>
    );
};

export default DoughnutExample;
