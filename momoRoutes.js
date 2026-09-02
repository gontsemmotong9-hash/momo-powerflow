const express = require('express');
const router = express.Router();
const momoService = require('./momoService');

// Route: Initiate Request to Pay
router.post('/collect-payment', async (req, res) => {
  const { amount, msisdn, orderId } = req.body;

  try {
    const result = await momoService.requestToPay({
      amount,
      msisdn,
      externalId: orderId,
      payerMessage: `Order ${orderId} Payment`,
      payeeNote: `Order ${orderId} Payment`,
    });

    res.status(202).json({
      message: 'Payment prompt sent to customer phone.',
      referenceId: result.referenceId,
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to initiate payment.' });
  }
});

// Route: Check Request to Pay Status
router.get('/payment-status/:referenceId', async (req, res) => {
  try {
    const statusData = await momoService.getPaymentStatus(req.params.referenceId);
    res.status(200).json(statusData);
  } catch (error) {
    res.status(500).json({ error: 'Failed to retrieve payment status.' });
  }
});

// Route: MoMo Callback Endpoint (Webhook)
router.post('/callback', (req, res) => {
  const transactionData = req.body;
  console.log('Received Callback:', transactionData);

  // Update order/transaction status in your database according to transactionData.status
  // E.g., 'SUCCESSFUL', 'FAILED', 'REJECTED'

  res.status(200).send();
});

module.exports = router;