import React from 'react';
import {Radar} from 'react-chartjs-2';

const data = {
  labels: ['Mode usage', 'Interaction', 'Rebound', 'Frequency', 'Task'],
  datasets: [
    {
      backgroundColor: 'rgba(179,181,198,0.2)',
      borderColor: 'rgba(179,181,198,1)',
      pointBackgroundColor: 'rgba(179,181,198,1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(179,181,198,1)',
      data: [65, 59, 90, 81, 56]
    },
  ]
};

const RadarExample = () => {
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
        <Radar data={data} options={options}/>
    );
};

export default RadarExample;