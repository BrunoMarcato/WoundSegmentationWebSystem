<template>
    <v-dialog :model-value="show" @update:model-value="updateShow" max-width="800px">
        <v-card>
            <v-card-title class="text-h5">Evolução da Área da Ferida</v-card-title>
            <v-card-text style="height: 400px;">
                <div v-if="chartData" style="height: 100%;">
                    <line-chart :data="chartData" :options="chartOptions" />
                </div>
                <div v-else>
                    <p class="text-center">Nenhuma imagem para gerar o gráfico.</p>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" text @click="fechar">Fechar</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { Line } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Filler
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

export default {
    components: {
        LineChart: Line
    },
    props: {
        group: {
            type: Object,
            required: true
        },
        show: {
            type: Boolean,
            required: true
        }
    },
    computed: {
        sortedImages() {
            if (!this.group || !this.group.images) return []
            return [...this.group.images].sort((a, b) => new Date(a.data) - new Date(b.data))
        },
        chartData() {
            const sorted = this.sortedImages
            return {
                labels: sorted.map(img => this.formatDate(img.data)),
                datasets: [
                    {
                        label: 'Área da Ferida (px²)',
                        data: sorted.map(img => img.area),
                        fill: true,
                        tension: 0.4,
                        borderColor: 'rgba(75,192,192,1)',
                        backgroundColor: 'rgba(75,192,192,0.2)',
                        pointBackgroundColor: 'rgba(75,192,192,1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(75,192,192,1)'
                    }
                ]
            }
        },
        chartOptions() {
            return {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1500,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#333',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        callbacks: {
                            title: (tooltipItems) => {
                                const index = tooltipItems[0].dataIndex
                                return this.sortedImages[index].name
                            },
                            label: (tooltipItem) => {
                                const value = tooltipItem.formattedValue
                                return `Área: ${value} px²`
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Data',
                            color: '#555',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            color: '#777'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Área da Ferida (px²)',
                            color: '#555',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            color: '#777'
                        },
                        grid: {
                            color: '#eee'
                        }
                    }
                }
            }
        }
    },
    methods: {
        fechar() {
            this.$emit('update:show', false)
        },
        updateShow(value) {
            this.$emit('update:show', value)
        },
        formatDate(dateStr) {
            const date = new Date(dateStr)
            return date.toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            })
        }
    }
}
</script>