// Mock store for use in testing

export default {
    state: {
        totalLogs: 1000,
        hostsInfo: [
            {
                key: 'winnie',
                value: 5648,
            },
            {
                key: 'yogi',
                value: 2730,
            },
        ],
        logsInfo: {
            docs: [],
            sizes: {
                file: 1000,
            },
        },
    },
}
