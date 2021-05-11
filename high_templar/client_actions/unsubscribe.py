async def unsubscribe(connection, message):
    """
    Unsubscribe by finding the subscription based on message.requestId.
    """
    if 'requestId' not in message:
        return await connection.send({
            'code': 'error',
            'message': 'no-request-id'
        })

    for subscription in connection.app.hub.subscriptions[connection]:
        if subscription.request_id == message['requestId']:
            connection.app.hub.unsubscribe(subscription)
            await connection.send({
                'code': 'success',
            })
            break
    else:
        return await connection.send({
            'code': 'error',
            'message': 'not-subscribed'
        })
