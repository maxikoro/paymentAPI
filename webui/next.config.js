module.exports = {
  async rewrites() {
    const isProd = process.env.NODE_ENV === 'production';
    const destinationBase = isProd ? 'http://main-api:8000' : 'http://127.0.0.1:8000';

    return [
      {
        source: '/payments',
        destination: `${destinationBase}/payments/`,
      },
      {
        source: '/payments/lp/:id',
        destination: `${destinationBase}/payments/lp/:id`,
      },
    ]
  },
}