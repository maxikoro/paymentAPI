import React from "react";
import Head from "next/head";
import Cookies from "js-cookie";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { Toast, ToastContainer, Spinner, OverlayTrigger, Tooltip } from "react-bootstrap";
import { v4 as uuidv4 } from 'uuid';


export default function Home() {
  const [uuid, setUuid] = React.useState("");
  const [accountNumber, setAccountNumber] = React.useState("");
  const [amount, setAmount] = React.useState("");
  const [paymentPurpose, setPaymentPurpose] = React.useState("");
  const [payments, setPayments] = React.useState([]);
  const [errors, setErrors] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const savedUuid = Cookies.get("uuid");
    if (savedUuid) {
      setUuid(savedUuid);
    } else {
      const newUuid = uuidv4();
      setUuid(newUuid);
      Cookies.set("uuid", newUuid);
    }
  }, []);

  React.useEffect(() => {
    payments.forEach(payment => {
      if (payment.state === "pending") {
        pollPaymentStatus(payment.paymentId);
      }
    });
  }, [payments]);

  const handleGenerateUUID = () => {
      const newUuid = uuidv4();
    setUuid(newUuid);
    Cookies.set("uuid", newUuid);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    const response = await fetch("/payments", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        userId: uuid,
        accountNumber: accountNumber,
        amount: amount,
        description: paymentPurpose,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Payment created:", data);
      setPayments([data, ...payments]);
      // setErrors([]);
    } else {
      const errorData = await response.json();
      console.error("Failed to create payment", errorData);
      setErrors([...errors, { id: uuidv4(), message: errorData.message || "Ошибка при создании платежа" }]);
    }
    setIsLoading(false);
  };

  const pollPaymentStatus = async (paymentId) => {
    try {
      const response = await fetch(`/payments/lp/${paymentId}`);
      if (response.ok) {
        const updatedPayment = await response.json();
        setPayments(prevPayments => prevPayments.map(payment => payment.paymentId === paymentId ? updatedPayment : payment));
      } else if (response.status === 408) {
        pollPaymentStatus(paymentId); // Retry on timeout
      }
    } catch (error) {
      console.error("Error polling payment status:", error);
    }
  };

  return (
    <>
      <Head>
        <title>Payment Pet Project</title>
        <meta name="description" content="Generated by create next app" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="container">
        <h1 className="mt-5">Привет, пользователь</h1>
        <div className="d-flex align-items-center">
          <span>Ваш UUID: {uuid}</span>
          <button className="btn btn-primary ms-2" onClick={handleGenerateUUID}>
            <i className="bi bi-arrow-repeat"></i>
          </button>
        </div>

        <div className="mt-3">
          <label>
            Номер счета (numeric):
            <input
              type="number"
              className="form-control"
              value={accountNumber}
              onChange={(e) => setAccountNumber(e.target.value)}
            />
          </label>
        </div>
        <div className="mt-3">
          <label>
            Сумма (numeric):
            <input
              type="number"
              className="form-control"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </label>
        </div>
        <div className="mt-3">
          <label>
            Назначение платежа (string):
            <input
              type="text"
              className="form-control"
              value={paymentPurpose}
              onChange={(e) => setPaymentPurpose(e.target.value)}
            />
          </label>
        </div>
        <button className="btn btn-success mt-3" onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? (
            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          ) : null}
          Отправить платеж
        </button>
        <div className="mt-5">
          <h2>Результаты платежей</h2>
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Payment ID</th>
                <th>UUID</th>
                <th>Дата создания</th>
                <th>Дата обработки</th>
                <th>Состояние</th>
                <th>Номер счета</th>
                <th>Сумма</th>
                <th>Назначение платежа</th>
                <th>Дополнительные детали</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment, index) => (
                <tr key={index}>
                  <td>{payment.paymentId}</td>
                  <td>{payment.userId}</td>
                  <td>{payment.created}</td>
                  <td>{payment.processed}</td>
                  <td>
                    {payment.state === "pending" ? (
                      <OverlayTrigger
                        placement="top"
                        overlay={<Tooltip id={`tooltip-${index}`}>{payment.state}</Tooltip>}
                      >
                        <Spinner animation="border" size="sm" />
                      </OverlayTrigger>
                    ) : payment.state === "completed" ? (
                      <OverlayTrigger
                        placement="top"
                        overlay={<Tooltip id={`tooltip-${index}`}>{payment.state}</Tooltip>}
                      >
                        <i className="bi bi-check-circle-fill text-success"></i>
                      </OverlayTrigger>
                    ) : payment.state === "rejected" ? (
                      <OverlayTrigger
                        placement="top"
                        overlay={<Tooltip id={`tooltip-${index}`}>{payment.state}</Tooltip>}
                      >
                        <i className="bi bi-x-circle-fill text-danger"></i>
                      </OverlayTrigger>
                    ) : (
                      payment.state
                    )}
                  </td>
                  <td>{payment.accountNumber}</td>
                  <td>{payment.amount}</td>
                  <td>{payment.description}</td>
                  <td>{payment.extPaymentDetails}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ToastContainer position="bottom-end" className="p-3">
          {errors.map((error) => (
            <Toast key={error.id} bg="danger" onClose={() => setErrors(errors.filter((e) => e.id !== error.id))} show={true} delay={3000} autohide>
              <Toast.Header>
                <strong className="me-auto">Ошибка</strong>
              </Toast.Header>
              <Toast.Body>{error.message}</Toast.Body>
            </Toast>
          ))}
        </ToastContainer>
      </div>
    </>
  );
}
