x <- read.csv('cluster_buys.csv')

# Rename the 'Price.Increase....' column to 'Price.Increase'
names(x)[names(x) == "Price.Increase...."] <- "Price.Increase"

# Filter out rows where Price.Increase is less than -50
x <- subset(x, !is.na(Price.Increase))
filtered_x <- subset(x, Price.Increase >= -50)

mean(x$Price.Increase)

plot(filtered_x$Price.Increase, filtered_x$Days.Since.Trade, 
     xlab = "Return on Investment (%)", 
     ylab = "Days Since Trade",
     main = "Insider Cluster Buys")
bf_line <- lm(Days.Since.Trade ~ Price.Increase, data = filtered_x)
abline(bf_line)

mean(filtered_x$Price.Increase)

my_lm <- lm(Price.Increase ~ Days.Since.Trade + Ins, data = x)

summary(my_lm)

my_lm2 <- lm(Price.Increase ~ Days.Since.Trade * Ins, data = x)

summary(my_lm2)
