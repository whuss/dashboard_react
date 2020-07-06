import React from 'react';
import {Radar} from 'react-chartjs-2';


const RadarExample = ({color, data}) => {
    const chartData = {
        labels: ['Mode usage', 'Interaction', 'Rebound', 'Frequency', 'Task'],
        datasets: [
          {
            backgroundColor: 'rgba(179,181,198,0.2)',
            borderColor: color,
            pointBackgroundColor: color,
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: color,
            data: data
          },
        ]
      };
      

    const options = {
        legend: {
            display: false,
        },
        scale: {
            ticks: {
                beginAtZero: true,
                min: 0,
                max: 100,
                stepSize: 25,
            }
        }
    };

    return (
        <Radar data={chartData} options={options}/>
    );
};

export default RadarExample;