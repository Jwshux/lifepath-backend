from flask_mail import Message

from ..extensions import mail


def send_account_recovery_email(
    recipient_email,
    username,
    reset_code,
):
    message = Message(
        subject='LifePATH Account Recovery',
        recipients=[recipient_email],
    )

    message.body = f"""Hi {username},

We received a request to recover your LifePATH account.

Username: {username}
Verification code: {reset_code}

This code expires in 10 minutes.

Never share this code with anyone. LifePATH will never ask you for it.

If you did not request this recovery, you can safely ignore this email.

— The LifePATH Team
"""

    message.html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>LifePATH Account Recovery</title>
      </head>

      <body
        style="
          margin: 0;
          padding: 0;
          background-color: #eee7dd;
          font-family: Arial, Helvetica, sans-serif;
          color: #3b2a20;
        "
      >
        <table
          role="presentation"
          width="100%"
          cellspacing="0"
          cellpadding="0"
          border="0"
          style="
            width: 100%;
            background-color: #eee7dd;
            padding: 32px 16px;
          "
        >
          <tr>
            <td align="center">
              <table
                role="presentation"
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                  width: 100%;
                  max-width: 560px;
                  background-color: #fbf8f3;
                  border: 1px solid #ddd2c5;
                  border-radius: 18px;
                  overflow: hidden;
                  box-shadow: 0 18px 40px rgba(56, 36, 23, 0.12);
                "
              >
                <!-- Top accent -->
                <tr>
                  <td
                    style="
                      height: 8px;
                      padding: 0;
                      background-color: #6f8464;
                      font-size: 0;
                      line-height: 0;
                    "
                  >
                    &nbsp;
                  </td>
                </tr>

                <!-- Header -->
                <tr>
                  <td
                    style="
                      padding: 32px 32px 18px;
                      text-align: center;
                    "
                  >
                    <div
                      style="
                        font-family: Georgia, 'Times New Roman', serif;
                        font-size: 28px;
                        line-height: 1;
                        color: #3b2a20;
                      "
                    >
                      Life<span
                        style="
                          font-family: Arial, Helvetica, sans-serif;
                          font-size: 18px;
                          font-weight: 700;
                          letter-spacing: 0.12em;
                          color: #6f8464;
                        "
                      >PATH</span>
                    </div>

                    <p
                      style="
                        margin: 12px 0 0;
                        font-size: 14px;
                        color: #7a685d;
                      "
                    >
                      Account Recovery
                    </p>
                  </td>
                </tr>

                <!-- Main content -->
                <tr>
                  <td style="padding: 8px 32px 38px;">
                    <p
                      style="
                        margin: 0 0 18px;
                        font-size: 16px;
                        line-height: 1.6;
                        color: #3b2a20;
                      "
                    >
                      Hi <strong>{username}</strong>,
                    </p>

                    <p
                      style="
                        margin: 0 0 24px;
                        font-size: 15px;
                        line-height: 1.7;
                        color: #5f4a3e;
                      "
                    >
                      We received a request to recover your LifePATH account.
                      Use the details below to continue.
                    </p>

                    <!-- Username card -->
                    <table
                      role="presentation"
                      width="100%"
                      cellspacing="0"
                      cellpadding="0"
                      border="0"
                      style="
                        width: 100%;
                        margin: 0 0 20px;
                        background-color: #f3eee7;
                        border: 1px solid #ddd2c5;
                        border-radius: 12px;
                      "
                    >
                      <tr>
                        <td style="padding: 18px 20px;">
                          <p
                            style="
                              margin: 0 0 6px;
                              font-size: 12px;
                              font-weight: 700;
                              letter-spacing: 0.04em;
                              color: #7a685d;
                            "
                          >
                            Username
                          </p>

                          <p
                            style="
                              margin: 0;
                              font-size: 17px;
                              font-weight: 700;
                              color: #3b2a20;
                            "
                          >
                            {username}
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Verification code -->
                    <table
                      role="presentation"
                      width="100%"
                      cellspacing="0"
                      cellpadding="0"
                      border="0"
                      style="
                        width: 100%;
                        margin: 0 0 24px;
                        background-color: #6f8464;
                        border-radius: 12px;
                      "
                    >
                      <tr>
                        <td
                          align="center"
                          style="padding: 28px 20px;"
                        >
                          <p
                            style="
                              margin: 0 0 10px;
                              font-size: 12px;
                              font-weight: 700;
                              letter-spacing: 0.08em;
                              text-transform: uppercase;
                              color: #eef3eb;
                            "
                          >
                            Verification Code
                          </p>

                          <p
                            style="
                              margin: 0;
                              font-family: 'Courier New', monospace;
                              font-size: 46px;
                              font-weight: 700;
                              line-height: 1;
                              letter-spacing: 0.28em;
                              color: #ffffff;
                            "
                          >
                            {reset_code}
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Expiration notice -->
                    <p
                      style="
                        margin: 0 0 18px;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #5f4a3e;
                      "
                    >
                      This verification code expires in
                      <strong style="color: #6f8464;">
                        10 minutes
                      </strong>.
                    </p>

                    <!-- Security reminder -->
                    <table
                      role="presentation"
                      width="100%"
                      cellspacing="0"
                      cellpadding="0"
                      border="0"
                      style="
                        width: 100%;
                        background-color: #f3eee7;
                        border-left: 4px solid #6f8464;
                        border-radius: 10px;
                      "
                    >
                      <tr>
                        <td style="padding: 16px 18px;">
                          <p
                            style="
                              margin: 0 0 8px;
                              font-size: 12px;
                              font-weight: 700;
                              letter-spacing: 0.06em;
                              text-transform: uppercase;
                              color: #6f8464;
                            "
                          >
                            Security reminder
                          </p>

                          <p
                            style="
                              margin: 0;
                              font-size: 13px;
                              line-height: 1.65;
                              color: #6f5b4f;
                            "
                          >
                            Never share this code with anyone. LifePATH will
                            never ask you for this code. If you did not request
                            account recovery, you can safely ignore this email.
                          </p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <!-- Footer -->
                <tr>
                  <td
                    style="
                      padding: 22px 32px 28px;
                      border-top: 1px solid #e5ddd4;
                      text-align: center;
                    "
                  >
                    <p
                      style="
                        margin: 0 0 6px;
                        font-size: 12px;
                        color: #8a776b;
                      "
                    >
                      The LifePATH Team
                    </p>

                    <p
                      style="
                        margin: 0;
                        font-size: 11px;
                        color: #a08f84;
                      "
                    >
                      lifepath-site.vercel.app
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    mail.send(message)