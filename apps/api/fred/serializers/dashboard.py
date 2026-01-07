"""Dashboard serializers."""

from rest_framework import serializers


class DashboardTotalRxReportSerializer(serializers.Serializer):
    """Serializer for the dashboard total RX report response."""

    rxToday = serializers.IntegerField()
    rxTodayDirect = serializers.IntegerField()
    rxTodayDelivers = serializers.IntegerField()
    rxTodayInOffice = serializers.IntegerField()
    rxThisMonth = serializers.IntegerField()
    rxThisMonthDirect = serializers.IntegerField()
    rxThisMonthDelivers = serializers.IntegerField()
    rxThisMonthInOffice = serializers.IntegerField()
    rxLastMonth = serializers.IntegerField()
    rxLastMonthDirect = serializers.IntegerField()
    rxLastMonthInOffice = serializers.IntegerField()


class DashboardTotalPaymentsReportSerializer(serializers.Serializer):
    """Serializer for the dashboard total payments report response."""

    paymentToday = serializers.CharField()
    paymentTodayDirect = serializers.CharField()
    paymentTodayDelivers = serializers.CharField()
    paymentThisMonth = serializers.CharField()
    paymentThisMonthDirect = serializers.CharField()
    paymentThisMonthDelivers = serializers.CharField()
    paymentLastMonth = serializers.CharField()
    paymentLastMonthDirect = serializers.CharField()
    paymentLastMonthDelivers = serializers.CharField()


class DashboardSmsReportBucketSerializer(serializers.Serializer):
    """Serializer for an SMS report bucket."""

    tasksComplete = serializers.IntegerField()
    tasks = serializers.IntegerField()
    success = serializers.IntegerField()
    attempted = serializers.IntegerField()


class DashboardSmsReportSerializer(serializers.Serializer):
    """Serializer for the dashboard SMS report response."""

    twentyFourHours = DashboardSmsReportBucketSerializer()
    thisMonth = DashboardSmsReportBucketSerializer()
    lastMonth = DashboardSmsReportBucketSerializer()


class DashboardRefillsReportSerializer(serializers.Serializer):
    """Serializer for the dashboard refills report response."""

    potentialRefills = serializers.IntegerField()
    avgRefills = serializers.FloatField()
    totalRefills = serializers.IntegerField()
    unpaidRefills = serializers.IntegerField()
    unpaidRefillsThisMonth = serializers.IntegerField()
    unpaidRefillsLastMonth = serializers.IntegerField()
    shippedRefills = serializers.IntegerField()
    shippedRefillsThisMonth = serializers.IntegerField()
    shippedRefillsLastMonth = serializers.IntegerField()


class DashboardProgramReportBucketSerializer(serializers.Serializer):
    """Serializer for a program report bucket."""

    program = serializers.CharField()
    totalRx = serializers.IntegerField()
    shipped = serializers.IntegerField()
    offices = serializers.IntegerField()
    unpaid = serializers.IntegerField()


class DashboardProgramReportSerializer(serializers.Serializer):
    """Serializer for the dashboard program report response."""

    pcdelivers = DashboardProgramReportBucketSerializer()
    pcdirect = DashboardProgramReportBucketSerializer()


class DashboardFulfillmentReportSerializer(serializers.Serializer):
    """Serializer for the dashboard fulfillment report response."""

    toFill = serializers.IntegerField()
    inFill = serializers.IntegerField()
    shipped = serializers.IntegerField()
    inNS = serializers.IntegerField()


class DashboardTrendSeriesSerializer(serializers.ListField):
    """Serializer for a list of [label, count] trend points."""

    child = serializers.ListField(child=serializers.JSONField())


class DashboardTrendsReportSerializer(serializers.Serializer):
    """Serializer for the dashboard trends report response."""

    rx = DashboardTrendSeriesSerializer()
    shipments = DashboardTrendSeriesSerializer()
    payments = DashboardTrendSeriesSerializer()


class DashboardSumsReportSerializer(serializers.Serializer):
    """Serializer for the dashboard sums report response."""

    rx = DashboardTrendSeriesSerializer()
    shipments = DashboardTrendSeriesSerializer()
    payments = DashboardTrendSeriesSerializer()
