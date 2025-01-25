module.exports = {
  async rewrites() {
    return [
      {
        source: '/payments',
        destination: 'http://127.0.0.1:8000/payments/',
      },
      {
        source: '/payments/lp/:id',
        destination: 'http://127.0.0.1:8000/payments/lp/:id',
      },
    ]
  },
}