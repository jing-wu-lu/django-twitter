class TweetPhotoStatus:
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'pending'),
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)
